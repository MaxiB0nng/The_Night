/*
 * The Night - ncurses port
 *
 * Single-file C rewrite of the original pygame project. The noise shader
 * and audio playback have no ncurses equivalent and are intentionally
 * dropped (see project discussion). The original PNG background art and
 * cutscene frames ARE shown, converted to colored half-block ("ANSI
 * art") glyphs by scratchpad/convert_art.py -- the source images are a
 * strict black/green duo-tone, confirmed by sampling every pixel, so
 * this is a faithful conversion rather than an approximation.
 *
 * Everything else -- state machine, cutscene sequencing/timing, item/
 * plot flags, choice-tree navigation, save/load -- behaves the same as
 * the Python original, using the same on-disk save formats.
 *
 * Build: gcc -std=c11 -O2 -o The_night.out The_night.c -lncursesw
 * (needs the *wide* ncurses build -- narrow ncurses can't place the
 * UTF-8 half-block glyphs the art renderer uses).
 */

#define _POSIX_C_SOURCE 200809L
#include <ncurses.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <ctype.h>
#include <signal.h>
#include <unistd.h>
#include <locale.h>

/* ---------------------------------------------------------------------
 * Files (same formats/paths as the Python version, for compatibility)
 * ------------------------------------------------------------------- */
#define SAVE_FILE     "save.tns"
#define SETTINGS_FILE "player.tnp"
#define LOG_FILE      "log.txt"
#define TREE_JSON_FILE "choice_tree.json"

/* ---------------------------------------------------------------------
 * UI layout (text-mode replacement for the 320x240 pixel canvas)
 * ------------------------------------------------------------------- */
#define UI_WIDTH   62
#define MAIN_H     11
#define STORY_H    3
#define CHOICE_H   4

#define COLOR_PAIR_NORMAL 1
#define COLOR_PAIR_MARKER 2
#define COLOR_PAIR_INV 3 /* black-on-green: used for half-block art */

/* One converted image: MAIN_H rows of UI_WIDTH characters each, using a
 * 4-symbol encoding that packs 2 vertical source samples per character
 * cell via half-block glyphs (see draw_art()):
 *   ' ' = both black   '#' = both green   '^' = upper green/lower black
 *   'v' = upper black/lower green
 * Generated from the original PNGs by scratchpad/convert_art.py -- the
 * source art is a strict black/green duo-tone (confirmed by sampling
 * every pixel), so this lossless-ish 2-color classification is faithful
 * to the original rather than an approximation. */
typedef const char *const ArtBlock[MAIN_H];

/* Top-left corner of each panel within stdscr, computed once at startup
 * (centered in the terminal). Populated by ui_layout_init(). */
static int g_main_top, g_main_left;
static int g_story_top, g_story_left;
static int g_choice_top, g_choice_left;
static int g_box_top, g_box_left; /* outer border box */

/* ---------------------------------------------------------------------
 * Time helper (replaces pygame.time.get_ticks(): ms since program start)
 * ------------------------------------------------------------------- */
static long long g_start_ms = 0;

static long long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    long long ms = (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
    return ms - g_start_ms;
}

/* ---------------------------------------------------------------------
 * Minimal JSON parser (object/array/string/number/bool/null) -- enough
 * to read choice_tree.json. Parses once at startup; memory isn't freed
 * since the process only ever runs once (same lifetime as image/font
 * assets the Python side loaded once at startup).
 * ------------------------------------------------------------------- */
typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JType;

typedef struct JValue JValue;
typedef struct { char *key; JValue *val; } JMember;

struct JValue {
    JType type;
    double num;
    int boolean;
    char *str;
    JValue **items;
    int count;      /* for arr/obj: number of items/members */
    JMember *members;
};

typedef struct {
    const char *p;
} JParser;

static void j_skip_ws(JParser *jp) {
    while (*jp->p && isspace((unsigned char)*jp->p)) jp->p++;
}

static JValue *j_new(JType t) {
    JValue *v = calloc(1, sizeof(JValue));
    v->type = t;
    return v;
}

static JValue *j_parse_value(JParser *jp);

static char *j_parse_raw_string(JParser *jp) {
    /* assumes *jp->p == '"' */
    jp->p++;
    size_t cap = 32, len = 0;
    char *buf = malloc(cap);
    while (*jp->p && *jp->p != '"') {
        char c = *jp->p++;
        if (c == '\\' && *jp->p) {
            char esc = *jp->p++;
            switch (esc) {
                case 'n': c = '\n'; break;
                case 't': c = '\t'; break;
                case 'r': c = '\r'; break;
                case '"': c = '"'; break;
                case '\\': c = '\\'; break;
                case '/': c = '/'; break;
                default: c = esc; break;
            }
        }
        if (len + 1 >= cap) { cap *= 2; buf = realloc(buf, cap); }
        buf[len++] = c;
    }
    if (*jp->p == '"') jp->p++;
    buf[len] = '\0';
    return buf;
}

static JValue *j_parse_string(JParser *jp) {
    JValue *v = j_new(J_STR);
    v->str = j_parse_raw_string(jp);
    return v;
}

static JValue *j_parse_number(JParser *jp) {
    const char *start = jp->p;
    if (*jp->p == '-') jp->p++;
    while (isdigit((unsigned char)*jp->p)) jp->p++;
    if (*jp->p == '.') { jp->p++; while (isdigit((unsigned char)*jp->p)) jp->p++; }
    if (*jp->p == 'e' || *jp->p == 'E') {
        jp->p++;
        if (*jp->p == '+' || *jp->p == '-') jp->p++;
        while (isdigit((unsigned char)*jp->p)) jp->p++;
    }
    JValue *v = j_new(J_NUM);
    v->num = strtod(start, NULL);
    return v;
}

static JValue *j_parse_array(JParser *jp) {
    JValue *v = j_new(J_ARR);
    jp->p++; /* [ */
    j_skip_ws(jp);
    size_t cap = 8;
    v->items = malloc(cap * sizeof(JValue *));
    v->count = 0;
    if (*jp->p == ']') { jp->p++; return v; }
    while (1) {
        j_skip_ws(jp);
        JValue *item = j_parse_value(jp);
        if ((size_t)v->count >= cap) { cap *= 2; v->items = realloc(v->items, cap * sizeof(JValue *)); }
        v->items[v->count++] = item;
        j_skip_ws(jp);
        if (*jp->p == ',') { jp->p++; continue; }
        if (*jp->p == ']') { jp->p++; break; }
        break; /* malformed, bail */
    }
    return v;
}

static JValue *j_parse_object(JParser *jp) {
    JValue *v = j_new(J_OBJ);
    jp->p++; /* { */
    j_skip_ws(jp);
    size_t cap = 8;
    v->members = malloc(cap * sizeof(JMember));
    v->count = 0;
    if (*jp->p == '}') { jp->p++; return v; }
    while (1) {
        j_skip_ws(jp);
        char *key = j_parse_raw_string(jp);
        j_skip_ws(jp);
        if (*jp->p == ':') jp->p++;
        j_skip_ws(jp);
        JValue *val = j_parse_value(jp);
        if ((size_t)v->count >= cap) { cap *= 2; v->members = realloc(v->members, cap * sizeof(JMember)); }
        v->members[v->count].key = key;
        v->members[v->count].val = val;
        v->count++;
        j_skip_ws(jp);
        if (*jp->p == ',') { jp->p++; continue; }
        if (*jp->p == '}') { jp->p++; break; }
        break;
    }
    return v;
}

static JValue *j_parse_value(JParser *jp) {
    j_skip_ws(jp);
    if (*jp->p == '"') return j_parse_string(jp);
    if (*jp->p == '{') return j_parse_object(jp);
    if (*jp->p == '[') return j_parse_array(jp);
    if (*jp->p == '-' || isdigit((unsigned char)*jp->p)) return j_parse_number(jp);
    if (strncmp(jp->p, "true", 4) == 0) { jp->p += 4; JValue *v = j_new(J_BOOL); v->boolean = 1; return v; }
    if (strncmp(jp->p, "false", 5) == 0) { jp->p += 5; JValue *v = j_new(J_BOOL); v->boolean = 0; return v; }
    if (strncmp(jp->p, "null", 4) == 0) { jp->p += 4; return j_new(J_NULL); }
    jp->p++; /* malformed input: skip a char to avoid an infinite loop */
    return j_new(J_NULL);
}

static JValue *json_parse(const char *text) {
    JParser jp = { text };
    return j_parse_value(&jp);
}

static JValue *j_get(JValue *obj, const char *key) {
    if (!obj || obj->type != J_OBJ) return NULL;
    for (int i = 0; i < obj->count; i++) {
        if (strcmp(obj->members[i].key, key) == 0) return obj->members[i].val;
    }
    return NULL;
}

static JValue *j_index(JValue *arr, int i) {
    if (!arr || arr->type != J_ARR || i < 0 || i >= arr->count) return NULL;
    return arr->items[i];
}

static const char *j_str(JValue *v) {
    if (!v || v->type != J_STR) return "";
    return v->str;
}

static int j_arr_count(JValue *v) {
    if (!v || v->type != J_ARR) return 0;
    return v->count;
}

static char *read_whole_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(size + 1);
    size_t got = fread(buf, 1, size, f);
    buf[got] = '\0';
    fclose(f);
    return buf;
}

/* ---------------------------------------------------------------------
 * log.py port
 * ------------------------------------------------------------------- */
static bool log_first = true;

static void log_write(const char *state, int valg, const char *valg_log) {
    time_t t = time(NULL);
    struct tm tmv;
    localtime_r(&t, &tmv);
    char timebuf[32];
    strftime(timebuf, sizeof timebuf, "%Y-%m-%d %H:%M:%S", &tmv);

    FILE *f = fopen(LOG_FILE, "a");
    if (!f) return;
    if (log_first) {
        fprintf(f, "log starts at %s.\n\n", timebuf);
    } else {
        fprintf(f, "%s: %s    %d  %s\n", timebuf, state ? state : "None", valg,
                valg_log ? valg_log : "None");
    }
    fclose(f);
    log_first = false;
}

static void log_write_close(void) {
    time_t t = time(NULL);
    struct tm tmv;
    localtime_r(&t, &tmv);
    char timebuf[32];
    strftime(timebuf, sizeof timebuf, "%Y-%m-%d %H:%M:%S", &tmv);

    FILE *f = fopen(LOG_FILE, "a");
    if (!f) return;
    fprintf(f, "%s  log closing\n=============================\n\n\n\n", timebuf);
    fclose(f);
}

/* ---------------------------------------------------------------------
 * audio.py port -- no sound backend in ncurses. Kept as text-only state
 * (current track name + volumes) so the Settings/Music menu still shows
 * meaningful values and can be adjusted, same as the original screen.
 * ------------------------------------------------------------------- */
typedef struct {
    const char *keys[3];
    int count;
    int index;      /* -1 = none playing */
    int volume;     /* 0..100 */
} MusicState;

static MusicState g_music = { { "start_up", "night", "home" }, 3, -1, 100 };
static int g_soundfx_volume = 100;

static const char *music_current(void) {
    return g_music.index >= 0 ? g_music.keys[g_music.index] : "none";
}

static void music_switch(const char *track_key) {
    for (int i = 0; i < g_music.count; i++) {
        if (strcmp(g_music.keys[i], track_key) == 0) { g_music.index = i; return; }
    }
}

static void music_next(int step) {
    if (g_music.index < 0) return;
    int n = g_music.count;
    int idx = ((g_music.index + step) % n + n) % n;
    g_music.index = idx;
}

static void music_set_volume(int v) {
    if (v < 0) v = 0;
    if (v > 100) v = 100;
    g_music.volume = v;
}

static void soundfx_set_volume(int v) {
    if (v < 0) v = 0;
    if (v > 100) v = 100;
    g_soundfx_volume = v;
}

static void soundfx_play(const char *key) { (void)key; /* no-op: no audio backend */ }

/* ---------------------------------------------------------------------
 * story_functions.py item/plot flag port
 * ------------------------------------------------------------------- */
typedef struct {
    const char *name;
    int ending;         /* unused elsewhere in the original code; kept only
                            for save-file index compatibility */
    bool happened;
} Item;

static Item item_list[3] = {
    { "bun", 0, false },
    { "knife", 6, false },
    { "letter", 6, false },
};
#define ITEM_COUNT 3

typedef struct {
    const char *name;
    int ending_a, ending_b; /* "alseep tv" stored (3,6) as a tuple in the
                                original; "asleep bed" stored a single int.
                                Neither is read anywhere else -- kept only
                                for fidelity. ending_b == -1 means "n/a". */
    bool happened;
} Plot;

static Plot plot_list[2] = {
    { "alseep tv", 3, 6, false },
    { "asleep bed", 1, -1, false },
};
#define PLOT_COUNT 2

static bool get_plot(const char *list_choice, const char *event_item) {
    if (strcmp(list_choice, "item") == 0) {
        for (int i = 0; i < ITEM_COUNT; i++)
            if (strcmp(item_list[i].name, event_item) == 0) return item_list[i].happened;
    } else if (strcmp(list_choice, "plot") == 0) {
        for (int i = 0; i < PLOT_COUNT; i++)
            if (strcmp(plot_list[i].name, event_item) == 0) return plot_list[i].happened;
    }
    return false;
}

static void plot_write(const char *list_choice, const char *event_item, bool val) {
    if (strcmp(list_choice, "item") == 0) {
        for (int i = 0; i < ITEM_COUNT; i++)
            if (strcmp(item_list[i].name, event_item) == 0) { item_list[i].happened = val; return; }
    } else if (strcmp(list_choice, "plot") == 0) {
        for (int i = 0; i < PLOT_COUNT; i++)
            if (strcmp(plot_list[i].name, event_item) == 0) { plot_list[i].happened = val; return; }
    }
}

/* ---------------------------------------------------------------------
 * cutsceen.py port: cutscene sequences (text + ASCII/half-block art).
 * The art is generated from the original PNGs (scratchpad/convert_art.py)
 * -- the source images are a strict black/green duo-tone, confirmed by
 * sampling every pixel, so this is a faithful conversion rather than an
 * approximation.
 * ------------------------------------------------------------------- */
#define DELAY_RANDOM -1

typedef enum { FR_FRAME, FR_FROM_TO } FrameType;

typedef struct {
    FrameType type;
    const char *text1, *text2, *text3; /* NULL = keep previous text (Python None) */
    int delay_ms;                      /* FR_FRAME: ms, or DELAY_RANDOM for "random" */
    int img_from, img_to;              /* FR_FRAME: img_from = 1-based index into the
                                           cutscene's img_list (0 = clear/green fill).
                                           FR_FROM_TO: 1-based [img_from,img_to] range,
                                           step count = img_to-img_from+1, matching the
                                           original's img_list[current_img-1] blit loop. */
} CutFrame;

#define FRAME(img, t1, t2, t3, d) { FR_FRAME, (t1), (t2), (t3), (d), (img), 0 }
#define FROMTO(a, b, d) { FR_FROM_TO, NULL, NULL, NULL, (d), (a), (b) }
#define FRAME_COUNT(arr) (int)(sizeof(arr) / sizeof((arr)[0]))

static const ArtBlock art_start_screen = {
    "                     vvv                                      ",
    "                 vv##^^       v#            #                 ",
    "     #         v####        v#####        ^###^               ",
    "  vv##vvv      ###^           ^#            ^                 ",
    "    ^#        ####                                #           ",
    "     ^        ####                     v        ^^#^^         ",
    "              #####                 vv##vv        ^           ",
    "         v    ^#####v                 ##                      ",
    "       vv##v   ^######vv     vv#^      ^                      ",
    "         #^      ^############^                               ",
    "                    ^^^^^^^^^                                 ",
};

static const ArtBlock art_kitchen_k = {
    "^^^#vvvv#^^   #       vv#^^^^#vv      #vvv     vv##vv         ",
    "  vv#^#       #    vv#^vv#v   v##     #v#^# vv#^    ^^^#vv    ",
    "#^^   #v    vv#vv#^#v########^^ #     #^### #^###vvv   vv##   ",
    "    # ## vv^#v#^   ^^######v    #     ^^#v# #    ^^^##^^  #   ",
    "    ^v##^#v^^       vv^^vv##    #v          #v      v#    #   ",
    "  v#^#v#^^       v#^^   ###^ v#^^^^^vvv     ##      ##    #   ",
    "#^vv##       vv#^ #       ####vv   v#^^^#vv #^      ##   #^   ",
    "#^####    vv##v   #    vv^^     ###vv   v#^^#       ##   #    ",
    " ####^ v#^^ ###   # v#^^^^vvvv#^^   ^###vv  #       ##   #    ",
    "   vv#^     ##^  v###     v###vv   v#^   ^^##v      ##   #    ",
    "vv#^         #v#^^  ^^#vv^^    ^###      v#^^^^#vvv ##vv##^#vv",
};

static const ArtBlock art_kitchen_uk = {
    "^^^#vvvv#^^   #       vv#^^^^#vv      #vvv     vv##vv         ",
    "  vv#^#       #    vv#^vv#v   v##     #v#^# vv#^    ^^^#vv    ",
    "#^^   #v    vv#vv#^#v########^^ #     #^### #^###vvv   vv##   ",
    "    # ## vv^#v#^   ^^######v    #     ^^#v# #    ^^^##^^  #   ",
    "    ^v##^#v^^       vv^^vv##    #v          #v      v#    #   ",
    "  v#^#v#^^       v#^^   ###^ v#^^^^^vvv     ##      ##    #   ",
    "#^vv#^       vv#^ #       ####vv   v#^^^#vv #^      ##   #^   ",
    "#^####    vv##v   #    vv^^     ###vv   v#^^#       ##   #    ",
    " ####^ v#^^ ###   # v#^^^^vvvv#^^   ^###vv  #       ##   #    ",
    "   vv#^     ##^  v###     v###vv   v#^   ^^##v      ##   #    ",
    "vv#^         #v#^^  ^^#vv^^    ^###      v#^^^^#vvv ##vv##^#vv",
};

static const ArtBlock art_livingroom = {
    "                       vvv#####     #   #vv                   ",
    "                  ####^^^^    #     #   # ^##vv               ",
    "        vv#^#     #           #     #   #^###v#               ",
    "        #####     #           #     #   #vv##^#vv###v         ",
    "        #####     #        vvv#     #     #####^^^  ^#        ",
    "        ####^     # vvv#^^^^  vvv###^#vv ##^^        #        ",
    "        ^         ^^    vvv#^^^  #^######^#          #        ",
    "                  vvv#^^^       #^   ^^## #          #        ",
    "           vvv#^^^              #       # #          #        ",
    "  vvv###^^^                     #       #v#          #vv      ",
    "v#^^^                           ^#vv    ###      vv#^^ ^^#vv  ",
};

static const ArtBlock art_sit_down = {
    "                                                              ",
    "   vvv                 v#########################             ",
    " v#####^#              #                       ##             ",
    " #v#### #              #                       ##             ",
    " v###v#v#              #                       ##             ",
    " ^###v###              #                       ##             ",
    "                       #                       ##             ",
    "                       #                       ##             ",
    "                       #vvvvvvvvvvvvvvvvvvvvvvv##             ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_room = {
    "                             vvvvvv                           ",
    "         #####^^^^^^^^v     #^     ^#                         ",
    "         # #^^^###^^^^^#    #v##^^^v#                         ",
    "         # #^^^^^##^^^##    ###^^^^^^^^#vv                    ",
    "^^^^^^^^^^##vvvvv##^^^#^^^^^####v        ^^#v                 ",
    "          ^#vvvvvvvv^^^      ^##^##v         ^#vv             ",
    "                               ^#v^##############             ",
    "                                 ^#v#           #             ",
    "                                   ^^^^^^^^^^^^^#v            ",
    "                                                  ^#v         ",
    "                                                    ^#vv      ",
};

static const ArtBlock art_lay_down_static = {
    "                                                        #^    ",
    "                                                       v#     ",
    "                                            #######v   #      ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####^^^^#  #      ",
    "                                            ####    #  #      ",
    "                                            ####    # v#^^^^#v",
    "                                             ^##vvvv##^      ^",
    "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#^^^^^^^^^^^^^^^^^^^^##         ",
    "                                                   #          ",
    "                                                   #v         ",
    "                                                    #v        ",
};

static const ArtBlock art_glitch_1 = {
    "##############################################################",
    "##############################################################",
    "##############################################################",
    "##############################################################",
    "v#############################################################",
    "##############################################################",
    "##############################################################",
    "##############################################################",
    "##############################################################",
    "##############################################################",
    "##############################################################",
};

static const ArtBlock art_glitch_2 = {
    " #############################################################",
    " #############################################################",
    " #############################################################",
    " ########################################################^####",
    "  ############################################################",
    " #############################################################",
    " ##########################################################^^^",
    " #^###########################################################",
    " #######################################################^####^",
    " #######################################################v#### ",
    " #############################################################",
};

static const ArtBlock art_glitch_3 = {
    " #############################################################",
    " ^^^#######################################################^  ",
    "    ###### ################################################   ",
    "    #####################################################^#vv ",
    "  ########################################################### ",
    " ############################################################ ",
    " ##########################################################^^ ",
    " #^##################################################^######  ",
    " #################################################### ##^###v ",
    " ####################################################v##v#### ",
    " #######^#################################################### ",
};

static const ArtBlock art_glitch_4 = {
    " #######^^^^^^^######################################         ",
    " ^^^####       ######################################vvvvvv   ",
    "    ######        #########################################   ",
    "    vvvvvvvvvvvvvv#######################################^^   ",
    "  ^^^^##################################################      ",
    "      ^#################################### ############ vvvv ",
    "       #################################### #######v#######^^ ",
    " #     ##############################################^^^^^^^  ",
    " ####################################################    vvvv ",
    " ^^##################################################vvvv#### ",
    "   ^^^^^^########################################^^^^^^^^^^^^ ",
};

static const ArtBlock art_glitch_5 = {
    " ^^^^^##^^^^^^^######################################         ",
    "     ###       ######################################         ",
    "     #####        ###################################         ",
    "    vvvvvvvvvvvvvv##################################v         ",
    "  ^^^^##################################################      ",
    "      ^^^^^################################ ############ vvvv ",
    "           ^^^^^^^^^#################^##### ###      ######^^ ",
    "               vvvvv################# #########      ^^^^^^^  ",
    "               ###########^###################^               ",
    "               ########### vvvvv##############vv              ",
    "         vvvvvv###########v#####################v             ",
};

static const ArtBlock art_glitch_6 = {
    " ^^^^ vv            ##########   ^^^^^^^^^###########         ",
    "     ###            ###################      ^^######         ",
    "     #####        #####################        ######         ",
    "    vvvvvvvvvvvvvv#############################v              ",
    "  ^^^^##########################################              ",
    "      ^^^^^################################ ####         vvvv ",
    "           ^^^^^^^^^####^#########^^^^##### ###      ######^^ ",
    "               vvvvv####v#########    #########      ^^^^^^^  ",
    "               ###########^###################^               ",
    "               ########### vvvvv###########^^^                ",
    "         vvvvvv####^^^^^^^v#########^^^^^^^                   ",
};

static const ArtBlock art_glitch_7 = {
    " ^^^^ vv            #  vvvvvvv   ^^^^^^^^^###########         ",
    "     ###            ##########               ^^######         ",
    "     #####        ############    #####        ######         ",
    "                  #######   ###   #######                     ",
    "                  ####^^^   ###      #####                    ",
    "              ########         vvvvvv###### ####         vvvv ",
    "              ^^^^^^##vv vvvvvv###^^^^##^^# ###      ######^^ ",
    "               vvvvv####v#########    ^^  ^^^^^      ^^^^^^^  ",
    "               ###########^#######                            ",
    "                        ## vv     vvvvvvvvv                   ",
    "         vvvvvvvvvv     ^^v##     ##^^^^^^^                   ",
};

static const ArtBlock art_glitch_8 = {
    "      vv            #       vv   ^^^^^^^^^                    ",
    "     ###            ###     ##               ^^######         ",
    "     #####            ###         #####        ######         ",
    "                      ###   ###   #######                     ",
    "                      ^^^   ###                               ",
    "              ####             vvvvvv       ####              ",
    "              ^^^^             ^^^^^^ vv  v ###               ",
    "                        vvvv          ^^  ^^^^^               ",
    "                        ##^# #####                            ",
    "                        ##                                    ",
    "                        ^^                                    ",
};

static const ArtBlock art_glitch_9 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_opening_cutsceen_1 = {
    "                                                              ",
    "   v#v             vv                      v    v##           ",
    "    ^          vv##^      vvv              ##           v     ",
    "              v##^         ^            vv###vv        ^#^    ",
    "             v###                         ###^^               ",
    "             ####            #     v       #^                 ",
    "       vv    #####v        v##     ##          v#v            ",
    "       ^^     ######vv  vv###^                  ^      vvv    ",
    "               #############^         vvv              ^^     ",
    " v##             ^^#####^^            ^^                      ",
    "                                                              ",
};

static const ArtBlock art_opening_cutsceen_2 = {
    "    v                                            vv           ",
    "   ^#^           vv#^                      #v   ^^^           ",
    "               v##^       ^##             v##          v#v    ",
    "              ###                       ^^#####         ^     ",
    "             ####            v            ^##                 ",
    "             ####v          v#     #v      ^    v             ",
    "       ##    ^#####v      v###     ^^          ^#^            ",
    "              ^#######vv#####                          ##^    ",
    "  vv           ^^#########^^          ##^                     ",
    " ^^^               ^^^^^                                      ",
    "                                                 v            ",
};

static const ArtBlock art_opening_cutsceen_3 = {
    "   ##v            vvv                      vv   ^#^           ",
    "               v##^       v#v              ##          vvv    ",
    "              v##^         ^            v#####v         ^     ",
    "             v###            v            ^##^                ",
    "             ####           v#     vv      #                  ",
    "       ##    ^####v        v##     ^^          v#v            ",
    "       ^      #######vvvv####                          v#v    ",
    "  v            ^###########^          v#v               ^     ",
    " ^#^             ^^^^^^^^^             ^                      ",
    "                                                              ",
    "                                vv              ##            ",
};

static const ArtBlock art_opening_cutsceen_4 = {
    "               v##^       v#v              ##          vvv    ",
    "              v##^         ^            v#####v         ^     ",
    "             v###            v            ^##^                ",
    "             ####           v#     vv      #                  ",
    "       #v    #####v        v##     #^          v#v            ",
    "       ^      #######vvvv####                   ^      v#v    ",
    "  v            ^###########^          v#v               ^     ",
    " ^#^             ^^^^^^^^^             ^                      ",
    "                                                              ",
    "                                 v              ##            ",
    "                                ^#^                           ",
};

static const ArtBlock art_opening_cutsceen_5 = {
    "              v##^         ^            v#####v        ^^^    ",
    "             v###            v            ^##^^               ",
    "             ####           v#     v       #^                 ",
    "       #v    #####v        v##     #^          v#v            ",
    "       ^^     ######vvvvvv###                   ^      v#v    ",
    "               ^###########^          v#v               ^     ",
    " ^##             ^^^###^^^             ^                      ",
    "                                                              ",
    "                                 v              ##            ",
    "                                ^#^              ^            ",
    "                                                              ",
};

static const ArtBlock art_opening_cutsceen_6 = {
    "             ####            v            ^##^                ",
    "             ####v          v#     vv      ^                  ",
    "       ##    ^####v       vv##     ^^          v#v            ",
    "              ^######vvv#####                          ##v    ",
    "  v            ^###########^          v#v                     ",
    " ^#^              ^^^^^^^              ^                      ",
    "         vv                                             v     ",
    "         ##v                    vv              ##     ##v    ",
    "       v####v         v         ^^^      v            #####v  ",
    "vvvvvvv#####vvvvvvvvvv##vvvvvvvvvvvvvvvv##vvvvvv#vvvvvv#####vv",
    "      #######        ####  v#^##^#v v######   v##v   #######  ",
};

static const ArtBlock art_opening_cutsceen_7 = {
    "             ####v          v#     vv      ^                  ",
    "       ##    ^####v       v###     ^^          ^#^            ",
    "              ^######vvv#####                          ##v    ",
    "  v            ^###########^          ##v                     ",
    " ^#^              ^^^^^^^                                     ",
    "                                                 v            ",
    "    ##                          vvv             ##          ##",
    "   v###           ##            ^^          ##             v##",
    "vvv#####vvvvvvvvv####vvvvvvvvvvvv#v#vvvv#vv####vvvvvvvvvvv####",
    "  #####v        v####v     v#^##^#v   v###v####v  v#      v###",
    " v#######       ^####   vv^^  ^^  ^#v ####v####^ v##v    #####",
};

static const ArtBlock art_opening_cutsceen_8 = {
    "       #^     #####vv    vv##^                 ^^^      v     ",
    "              ^#############^          v               ^#^    ",
    " v#v            ^#########^           ^#^                     ",
    "  ^                                                           ",
    "                                                vv            ",
    " v              #v              ##v            v^^            ",
    " ##           v###v                           v##v            ",
    "####vvvvvvvvvvv###vvvvvvvvv#vvvvvvvv#vvvvv#vvv####vvvvvvvvvvvv",
    "#####         #####v      v#^ ## ^##^   v###vv####v          #",
    "####^        ^^###^     v#^   ^^   ^#v  ##### v###   v       ^",
    "#####v         ^#^    v#^    vvvv    ^#v^###^^##^^  ##      v#",
};

static const ArtBlock art_opening_cutsceen_9 = {
    "  v            ^###########^          v#v                     ",
    " ^#^              ^^^^^^^              ^                      ",
    "                                                              ",
    "           v#v                  vv              ## ##         ",
    "          v###v        v        ^^^   vv          ####v       ",
    "vvvvvvvvvv#####vvvvvvv###vvvvvvvvvvv#v##vvvv##vvvv####vvvvvvvv",
    "         ######v      ##^ v#^ ## ^######^ v####vv######v      ",
    "        ^^^##^^^        v#^   ##   ^#v    ######^^^##^^^      ",
    "          v###v       v^^     ^^     ^#v ^######v ####        ",
    "                    v^       ####      ^#v ^###^              ",
    "                  v#        v####v       ^###^^         ##    ",
};

static const ArtBlock art_opening_cutsceen_10 = {
    "  ^                                                           ",
    "           v#                                   vv ##         ",
    "          v###v         v       v#v             ^#v###v       ",
    "vvvvvvvvvv####vvvvvvvvvv##vvvvvvv#vvvv##vvvvv#vvvv#####vvvvvvv",
    "         ^#####        ### v^ ^^^#v#####^  v###  ######       ",
    "        ^#####^^        v#^   ##  ^^##^   ^####^^^^####^      ",
    "          v###v       v#^     ^^     ^#v ^######v v###        ",
    "            ^       v#^      vvvv      ^#v^^###^^  ^^         ",
    "                  v#^       v####v       ^#####         ##    ",
    "vv              v#^         ######         ^#v         ###    ",
    "#^            v#^           vvvvvv           ^#v      v###v   ",
};

static const ArtBlock art_opening_cutsceen_11 = {
    "  ^       v                                             v     ",
    "         ##v                                    vv     v##    ",
    "       v####v        v          v#v      v      ^#    v####v  ",
    "vvvvvvvv####vvvvvvvv###vvvvvvvvvv#vvvvvv###vvvvv#vvvvvv####vvv",
    "       ######^     v###v   v^ ##^#v #######v  v###   ^######^ ",
    "      #########     ^^^ v#^   vv  ^^###^^^^  ###### #########v",
    "         ##v          v#^    v##v    ^#v    vv#####v   v##    ",
    "        #^###       v#^      ^^^^      ^#v  vv#####vv ###^#   ",
    "                  v#^       v####v       ^#v ^^###^^          ",
    "                v#^         ######         ^#v####v           ",
    "              v#^           ######           ^#v              ",
};

static const ArtBlock art_opening_cutsceen_12 = {
    "  ^                                                           ",
    "    ##            v                         v   vv          ##",
    "   v###          v##v           v#v        v##v ^#         ###",
    "vv######vvvvvvvvv####vvvvvvv#vvvv###vvvv#vv####vvvvvvvvvvv####",
    "  #####v        v####v     v^ ##^#v   v###v####v  v#      v###",
    " #######^        v##v   v#^   ##  ^^#v#####v##v  v##v    ^####",
    " v######vv            v#^    v##v    ^####^ ^   v####v  vv####",
    "##########          v#^      ####      ^##    ^#######^ ######",
    "   v##v           v#^                    ^#v  vv######vv    ##",
    "  v####v        v#^         ######         ^#v #########v v###",
    "    ^^        v#^           ######           ^#########^^   ^^",
};

static const ArtBlock art_opening_cutsceen_13 = {
    "  ^                                                           ",
    "                v                              vvv            ",
    " #v            v##              v#v           v###            ",
    "v###vvvvvvvvvv#####vvvvvvvvvvvvvv#vv#vvvvv#vvv####vvvvvvvvvvvv",
    "####v         #####       ^#^ #v^###^^   ###vv####           v",
    "####^        ^^##^^^    v#^   ##  ^^#v  #####^###^^          ^",
    "#####v         ###    v#^    vvvv    ^#v########^^  ##      v#",
    "#####^              v#^      ####      ^####       v###     ^#",
    "######v           v#^        ####        ^#v     vv#####v  v##",
    "#######^        v#^                        ^#v  ^######## ^###",
    "###           v#^           ######           ^#vvv######vv    ",
};

static const ArtBlock art_opening_cutsceen_14 = {
    "  ^                                                           ",
    "           v#                                   vv ##         ",
    "          v###v         v       v#v             ^#v###v       ",
    "vvvvvvvvvv####vvvvvvvvvv##vvvvvvv#vvvv##vvvvv#vvvv#####vvvvvvv",
    "         ^#####        ### v^ ^^^#######^  v###  ######       ",
    "        ^#####^^        v#^   ##  ^^##^   ^####^^^^####^      ",
    "          v###v       v#^     ^^     ^#v ^######v v###        ",
    "            ^       v#^      vvvv      ^#v^^###^^  ^^         ",
    "                  v#^       v####v       ^#####         ##    ",
    "vv              v#^         ######         ^#v         ###    ",
    "#^            v#^           vvvvvv           ^#v      v###v   ",
};

static const ArtBlock art_opening_cutsceen_15 = {
    "  ^       v                                             v     ",
    "         ##v                                    vv     v##    ",
    "       v####v        v          v#v      v      ^#    v####v  ",
    "vvvvvvvv####vvvvvvvv###vvvvvvvvvv#vvvvvv###vvvvv#vvvvvv####vvv",
    "       ######^     v###v   v^ ##^##^########^^####^#v#######^^",
    "      #########     ^^^ v#^   vv  ^^###^^^^  ###### #########v",
    "         ##v          v#^    v##v    ^#v    vv#####v   v##    ",
    "        #^###       v#^      ^^^^      ^#v  vv#####vv ###^#   ",
    "                  v#^       v####v       ^#v ^^###^^          ",
    "                v#^         ######         ^#v####v           ",
    "              v#^           ######           ^#v              ",
};

static const ArtBlock art_opening_cutsceen_16 = {
    "  ^                                                           ",
    "    ##            v                         v   vv          ##",
    "   v###          v##v           v#v        v##v ^#         ###",
    "vv######vvvvvvvvv####vvvvvvv#vvvv#vvvvvv#vv####vvvvvvvvvvv####",
    "  #####v        v####v     v^ ##^##^#vv#########^#v#vvv#######",
    " #######^        v##v   v#^   ##  ^^#v########v  v##v    ^####",
    " v######vv            v#^    v##v    ^####^ ^   v####v  vv####",
    "##########          v#^      ####      ^##    ^#######^ ######",
    "   v##v           v#^                    ^#v  vv######vv    ##",
    "  v####v        v#^         ######         ^#v #########v v###",
    "    ^^        v#^           ######           ^#########^^   ^^",
};

static const ArtBlock art_opening_cutsceen_17 = {
    "  ^                                                           ",
    "                v                              vvv            ",
    " #v            v##              v#v           v###            ",
    "v###vvvvvvvvvv#####vvvvvvvvvvvvvv#vvvvvvvv#vvv####vvvvvvvvvvvv",
    "####v         #####       ^#^ #v^##vv#^^####vv####^^^^^^^^^^^#",
    "####^        ^^##^^^    v#^   ##  ^^#v#^#########^^^^^^^^^^^^^",
    "#####v         ###    v#^    vvvv    ^#v########^^  ##      v#",
    "#####^              v#^      ####      ^####       v###     ^#",
    "######v           v#^        ####        ^#v     vv#####v  v##",
    "#######^        v#^                        ^#v  ^######## ^###",
    "###           v#^           ######           ^#vvv######vv    ",
};

static const ArtBlock art_opening_cutsceen_18 = {
    "  ^                                                           ",
    "           v#                                   vv ##         ",
    "          v###v         v       v#v             ^#v###v       ",
    "vvvvvvvvvv####vvvvvvvvvv##vvvvvvv#vvvvvvvvvvv#vvvv#####vvvvvvv",
    "         ^#####        ### v^ ^^^#vvvvvvvvvv###vv######vvvvvvv",
    "        ^#####^^        v#^   ##  ^^#v vvv##############vvvvvv",
    "          v###v       v#^     ^^     ^## ^######v v###        ",
    "            ^       v#^      vvvv      ^#v^^###^^  ^^         ",
    "                  v#^       v####v       ^#####         ##    ",
    "vv              v#^         ######         ^#v         ###    ",
    "#^            v#^           vvvvvv           ^#v      v###v   ",
};

static const ArtBlock art_opening_cutsceen_19 = {
    "  ^       v                                             v     ",
    "         ##v                                    vv     v##    ",
    "       v####v        v          v#v             ^#    v####v  ",
    "vvvvvvvv####vvvvvvvv###vvvvvvvvvv#vvvvvvvvvvvvvv#vvvvvv####vvv",
    "       ######^     v###v   v^ ##^#vvv vv vvvvvv###vvv######## ",
    "      #########     ^^^ v#^   vv  ^^##^^^^   ######v##########",
    "         ##v          v#^    v##v    ^#v#^^^#v#####v ^^###^^^^",
    "        #^###       v#^      ^^^^      ^#v  vv#####vv ###^#   ",
    "                  v#^       v####v       ^#v ^^###^^          ",
    "                v#^         ######         ^#v####v           ",
    "              v#^           ######           ^#v              ",
};

static const ArtBlock art_opening_cutsceen_20 = {
    "  ^                                                           ",
    "    ##            v                             vv          ##",
    "   v###          v##v           v#v             ^#         ###",
    "vv######vvvvvvvvv####vvvvvvv#vvvv###vvvvvvvvvvvvvvvvvvvvvv####",
    "  #####v        v####v     v^ ##^#v               v#      v###",
    " #######^        v##v   v#^   ##  ^^##^^^^^^^^^^^####^^^^^####",
    " v######vv            v#^    v##v    ^#v   vvvvvv####vvvvv####",
    "##########          v#^      ####      ^##^   ^#######^ ######",
    "   v##v           v#^                    ^#v  vv######vv    ##",
    "  v####v        v#^         ######         ^#v #########v v###",
    "    ^^        v#^           ######           ^#########^^   ^^",
};

static const ArtBlock art_opening_cutsceen_21 = {
    "  ^                                                           ",
    "                v                               vv            ",
    " #v            v##              v#v             ^#            ",
    "v###vvvvvvvvvv#####vvvvvvvvvvvvvv#vv#vvvvvvvvvvvvvvvvvvvvvvvvv",
    "####v         #####       ^#^ #v^###^^                       v",
    "####^        ^^##^^^    v#^   ##  ^^#vvvvvvvvvvvvvv    vvvvvv#",
    "#####v         ###    v#^    vvvv    ^#v          ^^##^^    v#",
    "#####^              v#^      ####      ^#v   vvvv  v###vvvvv##",
    "######v           v#^        ####        ^##^^   #######v  v##",
    "#######^        v#^                        ^#v  ^######## ^###",
    "###           v#^           ######           ^#vvv######vv    ",
};

static const ArtBlock art_opening_cutsceen_22 = {
    "                               v                              ",
    "^^#vvv                        ^#                       vvv#^^^",
    "     ^^^#vvv                                    vvv#^^^^v###vv",
    "           ^^^#vv                    vvvvvvv#^^^^ v   vv#####^",
    "###vvv           ^^#vvv        vvvv#^^           ####^^^######",
    " ^^^^^^               ^^^^###^^^         vvvvvv###### ########",
    "                            ^^^#vv    #^^^    vv#####v   ###  ",
    "              #####vvv            ^^##vv       v######^ ^##^^ ",
    "vv               ^^^#####vvv           ^^^^vvv   ###          ",
    " ^^^vvv                ^^^#####v             ^^^####^         ",
    "      ^^^#vvv                   vvvvvvvvv          ^^^vvvv    ",
};

static const ArtBlock art_opening_cutsceen_23 = {
    "      v                             v##                       ",
    "     ^#^                                       v         v    ",
    "    v#                       vv               ###v      ^#^   ",
    "v#vv###vvvvvvvvvvvvvvvvvvvvvv##vvvvvvvvvvv#vvv####vvvvvvvvvvvv",
    "######^                     #^#v        v### #####v           ",
    "^##^^^                    v#^  ^#      v##### ###^            ",
    "                        v#^      ^v    ^^###^^^^^^            ",
    "                    vv#^^          ^#v   ###                  ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
    "                                                              ",
    "             vvvvvvvvvvvvvvv               vvvvvvvvvvvvvvv    ",
};

static const ArtBlock art_opening_cutsceen_24 = {
    "      v                             v##                       ",
    "     ^#^                     v                     v     v    ",
    "    v                       ###v                  ##v   ^#^   ",
    "vvvv##vvvvvvvvvvvvvvvvvvvvvv####vvvvvvvvvvvvvvvvv#####vvvvvvvv",
    "#######                    #^  #           ##v  ######        ",
    "###^^^                    v#   ^#        v####vv######v       ",
    "^^^                      #^     ^#      vv####v ^^##^^^       ",
    "                        #^       ^#v     ####### ####         ",
    "                      v^           ^#     ^###^               ",
    "                  vv#^               #v   ^##^                ",
    "             vvvv#^                   ^^#vv                   ",
};

static const ArtBlock art_opening_cutsceen_25 = {
    "      v                     v#v     v##                       ",
    "     ^#^                  v##v##v                        v    ",
    "   v                      # vvv #                       ^#^vv ",
    "vvv##vvvvvvvvvvvvvvvvvvvvv# # # #vvvvvvvvvvvvvvvvvvvvvvvvvv###",
    "# ###v                   v#^^^^^#v                       v####",
    "##^##^                  v#       #               #v      #####",
    "#^ ^^                  v#         #v            ###v    ^#####",
    "^                     v#           #v         v#####v vv######",
    "                    v#^             ^#v       ####### ^^^^^###",
    "                 vv^^                 ^#v    ^########v   v###",
    "           vvvv#^                       ^#vvvv#########  ^^#^^",
};

static const ArtBlock art_opening_cutsceen_26 = {
    "      v                  v#^   ^v   v##                       ",
    "     ^#^               v##vvvvvvv#v                      v    ",
    "                       #    vvv   #                     ^#^   ",
    "v#vvvvvvvvvvvvvvvvvvvvv#   #   #  #vvvvvvvvvvvvvvvvv vvvvvvvvv",
    "###v                   #   #  ##  #                           ",
    "####                   #vvv#vvv#vv#                           ",
    "####^                 v#           #                        vv",
    "^#^                   #            #v                         ",
    "                     #^             #v                 ##     ",
    "                    #^               #v               v###    ",
    "                   #^                 #v             v####v   ",
};

static const ArtBlock art_opening_cutsceen_27 = {
    "                          #     v    ##                       ",
    "     ^#^               vv#vvv vvv#v                      v    ",
    "                       #    vvv   #                      #^   ",
    " v   vvvvvvvvvvvvvvvvvv#   #   #  #vvvvvvvvvvvvvvvvvvvvvvvvvvv",
    "^##                    #   #  ##  #                           ",
    "####                   vvvv#vvv#vv#                           ",
    "^###^                 v#           #                          ",
    "^#^                   v            #v                         ",
    "                     #^             #v                        ",
    "                    #^               #                        ",
    "                   v^                 vv                      ",
};

static const ArtBlock art_opening_cutsceen_28 = {
    "                         v#    ^v    ##                       ",
    "     ^#^                ##vvv vvv#v                      v    ",
    "                       #    vvv   #                      ^#   ",
    " #vvvvvvvvvvvvvvvvvvvvv#   #   #  #vv vv  vvvvvvv vvvvvvvvv   ",
    "###                    #   #  ##  #                    vv vvvv",
    "####                   #vvv#vvv#vv#                           ",
    "^^v#                  v#           #                          ",
    " v^                   #            #v                         ",
    "                     v^             #v                        ",
    "                    v^               #v                       ",
    "                   v^                 #v                      ",
};

static const ArtBlock art_opening_cutsceen_29 = {
    "                          ^          ^^                       ",
    "      #^                ^#vvv vv  v                           ",
    "                       #    v v                          ^#   ",
    " v             v vvvvvvv                        v  vvv        ",
    " #^                        v  ^                               ",
    " #                      v  v v  vvv                           ",
    "^                     vv                                      ",
    " v                                  v                         ",
    "                                    ^                         ",
    "                    v                                         ",
    "                   v^                 vv                      ",
};

static const ArtBlock art_opening_cutsceen_30 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_look_for_food1 = {
    "#######################################################       ",
    "                       #                             ##       ",
    "                       #                             ##       ",
    "                       #                             ##       ",
    "                       #                             ##       ",
    "                    vv #  v                          ##       ",
    "                    ## #  #                          ##       ",
    "                    ## #  #                          ##       ",
    "                     ^ #  ^                         v##       ",
    "                       #                            #v^       ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        ",
};

static const ArtBlock art_H_look_for_food2 = {
    "#######################################################       ",
    "                       ##^^^^^                       ##       ",
    "                       ##                            ##       ",
    "                       ##                            ##       ",
    "                       ##                            ##       ",
    "                    vv ##  v                         ##       ",
    "                    ## ## ##                         ##       ",
    "                    ## ## ##                         ##       ",
    "                     ^ ## ^^                        v##       ",
    "                       ##                           #v^       ",
    "^^^^^^^^^^^^^^^^^^^^^^^^#vvvvvvvvvvvvv#^^^^^^^^^^^^^^^        ",
};

static const ArtBlock art_H_look_for_food3 = {
    "#######################################################       ",
    "                       #  #                      v#^^##       ",
    "                       #  #                  vv#^    ##       ",
    "                       #  #               v#^^       ##       ",
    "                       #  #           vv#^^          ##       ",
    "                    vv #  #          #^              ##       ",
    "                    ## #  #          #               ##       ",
    "                    ## #  #          #               ##       ",
    "                     ^ # v#^^^^^^^^^^#              v##       ",
    "                       ##^           # ##           #v^       ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^# ##          v#^        ",
};

static const ArtBlock art_H_look_for_food4 = {
    "#######################################################       ",
    "                       #  #                          #^v      ",
    "                       #  #                          # ^#v    ",
    "                       #  #                          #   ^#v  ",
    "                       #  #                          #     ^#v",
    "                    vv #  #                          #       #",
    "                    ## #  #                          #       #",
    "                    ## #  #               vvvvvvvvvvv#       #",
    "                     ^ # v#^^^^^^^^^^^^^^^#^^^^#    v#       #",
    "                       ##^                ^^^^^^    #        #",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#vv     #",
};

static const ArtBlock art_H_look_for_food5 = {
    "#######################################################       ",
    "                       #  #                          #^v      ",
    "                       #  #                          # ^#v    ",
    "                       #  #                          #   ^#v  ",
    "                       #  #                          #     ^#v",
    "                    vv #  #                          #       #",
    "                    ## #  #                          #       #",
    "                    ## #  #               vvvvvvvvvvv#       #",
    "                     ^ # v#^^^^^^^^^^^^^^^^         v#       #",
    "                       ##^                          #        #",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#vv     #",
};

static const ArtBlock art_H_search1 = {
    "             #                                           #    ",
    "^^^^^^^^^^^^^^                                           #    ",
    "                                                         #    ",
    "                                                         #    ",
    "                                         vvv             #    ",
    "                                         #^^             #    ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####^^^^^^^^^^^^^^#v   ",
    "                                 ##^^^^^^^^^^^^^^##       ##v ",
    "                                  ^^^^^^^^^^^^^^^^^^       ^#v",
    "^^^^^^^#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#^^^^^^^^^^^^^^^^^^^^^^",
    "       #                               #                      ",
};

static const ArtBlock art_H_search2 = {
    "        ### #                   #                             ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                             ",
    "                                                              ",
    "                                                              ",
    "                                                            vv",
    "                                                            #^",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####",
    "                                                    ##^^^^^^^^",
    "                                                     ^^^^^^^^^",
    "^#^^^^^^^^^^^^^^^^^^^^^^^^#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#^^^",
    " #                        #                               #   ",
};

static const ArtBlock art_H_search3 = {
    "  #      #                       ### #                   #    ",
    "  #      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ",
    "  #                                                           ",
    "  #                                                           ",
    "  #           vv                                              ",
    "  #      vvvvv##vv                                            ",
    " v#^^^^^^#^^^^^^#^#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
    " #^      #      ^##                                           ",
    "#^       ^^^^^^^^^                                            ",
    "#^^^^^^^^^^^^^^^^^^^^^^^^^#^^^^^^^^^^^^^^^^^^^^^^^^#^^^^^^^^^^",
    "#                         #                        #          ",
};

static const ArtBlock art_H_tv1 = {
    "                                                              ",
    "   vvv                 v#########################             ",
    " v#####^#              # vvvvvvvvvvv  v#^^#    ##             ",
    " #v#### #              # ###v####v##  #   v#   ##             ",
    " v###v#v#              # ###########   #^^#    ##             ",
    " ^###v###              # ######v####  #^  ^v   ##             ",
    "                       #             v#    #   ##             ",
    "                       ###########^^^^^^^^^^^^^##             ",
    "                       ###########vvvvvvvvvvvvv##             ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_tv2 = {
    "                                                              ",
    "                                                              ",
    "                       # vvvvvvvvvvv  v#^^#    vv             ",
    "  v#### #              # ###v####v##  #   v#   ##             ",
    "  ^##v#v#              # ###########   #^^#    ##             ",
    "    ^ ###              # ######v####  #^  ^v   ##             ",
    "                       #             v#    #   ##             ",
    "                       ###########^^^^^^^^^^^^^##             ",
    "                        ^^^^^^^^^              ^^             ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_tv3 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "   vvvvv#              # ###########   #^^v    vv             ",
    "       ^^              # ######v####  #^  ^v   ##             ",
    "                       ^              ^    ^   ^^             ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_tv4 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_lay_down1 = {
    "                                                              ",
    "                           vvvvvvvv                           ",
    "      #####^^^^^^^^#v      #      ^^v                         ",
    "      # #^^^^###^^^^^#     # v#^^#v #                         ",
    "      # #vvvvvvvvvvvv#     ###^#vvv##vvvv                     ",
    "vvvvvv# #     ^^     #vvvvv####v        ^^#v                  ",
    "       ##^^^^^##^^^^^#     ^#^##vvv         ^#vv              ",
    "        ^^^^^^^^^^^^^^       ^v^#v## v vv  vvvv^^#            ",
    "                              ^#v ^^#^^^^^^#vvvv##            ",
    "                                ^#vv^            #            ",
    "                                  ^#vvvvvvvvvvvvv#            ",
};

static const ArtBlock art_H_lay_down2 = {
    "                                                              ",
    "                                                              ",
    "^^^^^^^#v              #             v                        ",
    "  vvvvvv##v            #      vvvv   #                        ",
    "##v       #            #    ##^   ^#v#                        ",
    "vvvvvvvvvv#            #####^^^^#vvv#^#vvv                    ",
    "^^^       #            #  #^v            ^^^#vv               ",
    "          #vvvvvvvvvvvv#  #v  #v              ^^#v            ",
    "###^^^^^^^#             ^v ^^#v  v               ^^vv         ",
    "vvvvvvvvvv#               #v  ^#v^^ v               ^^^#vv    ",
    "                           ^#v  ^^vv^^vvvv vvv   vvv vvv ^#   ",
};

static const ArtBlock art_H_lay_down3 = {
    "                                                        #^    ",
    "                                                       v#     ",
    "                                            #######v   #      ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####^^^^#  #      ",
    "                                            ####    #  #      ",
    "                                            ####    # v#^^^^#v",
    "                                             ^##vvvv##^      ^",
    "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#^^^^^^^^^^^^^^^^^^^^##         ",
    "                                                   #          ",
    "                                                   #v         ",
    "                                                    #v        ",
};

static const ArtBlock art_H_lay_down4 = {
    "                                                        v     ",
    "                                                       v#     ",
    "                                            #######v   #      ",
    "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####^^^^#  #      ",
    "                                            ####    #  #      ",
    "                                            ####    # v#^^^^#v",
    "                                             ^##vvvv##^      ^",
    "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#^^^^^^^^^^^^^^^^^^^^##         ",
    "                                                   #          ",
    "                                                   #v         ",
    "                                                    ^         ",
};

static const ArtBlock art_H_lay_down5 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                            v vv    v  v      ",
    "                                            ####    #  #      ",
    "                                            ####    # v#^^^^#v",
    "                                             ^##vvvv##^      ^",
    "             vvvvvvvvvvvvvvvvv#^^^^^^^^^^^^^^^^^^^^##         ",
    "                                                   ^          ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_lay_down6 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "                                                              ",
};

static const ArtBlock art_H_look_around_letter1 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    "           vvvvvv#####^^^^^^^^^^^^^^#vvvv                     ",
    "           #  ^^#^^^^^^^^^^^^^^^^^^^^^^^^#                    ",
    "           #    #          ^^^^          #                    ",
    "           #    #vvvvvvvvvvvvvvvvvvvvvvvv#                    ",
    "           #    #          vvvvv         #                    ",
    "           #    #                        #                    ",
    "           #    #vvvvvvvvvvvvvvvvvvvvvvvv#                    ",
    "           #    #           vvvv         #                    ",
};

static const ArtBlock art_H_look_around_letter2 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    " ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#v             ",
    " ##v           vvv#v                            ^#v           ",
    " # #v     vv#^^^ #^^^v                            ^#          ",
    " #  #v  ##^^^^^vv#  v#^                            ^#v        ",
    " #   #v  ^#v     v#^^                                ^#       ",
    " #    ^v   ^#vv#^                                      ^v     ",
    " #     ^#    ^                                          ^#v   ",
    " #      #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#   ",
};

static const ArtBlock art_H_look_around_letter3 = {
    "                                                              ",
    "                                                              ",
    "                                                              ",
    " ##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#v             ",
    " ##v      v#^^^####v                            ^#v           ",
    " # #v   v##vv#^^v^ ^^v                            ^#          ",
    " #  #v  ##^^#vv#^   v#^                            ^#v        ",
    " #   #v  ^#v     v#^^                                ^#       ",
    " #    ^v   ^#vv#^                                      ^v     ",
    " #     ^#    ^                                          ^#v   ",
    " #      #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#   ",
};

static const ArtBlock art_H_letter = {
    "       ####^###^^#^^^^^^^^^^^^#vvvvvvvvvvvvvvvvvvv^#          ",
    "       #### #######                                #          ",
    "       #vvvvvvvv vvvv vvvvvvvvvvvvvvvvvvvvvv       #          ",
    "       #^^^^^^^^ #^^^ #^^^##^^^ ^^^^^^^^^^^^^      #          ",
    "       ############# ################### ######    #          ",
    "       # #vv#vvv## ##vv^## #vvv    ^               #          ",
    "       # ^^^^^^ ^^ ^##^^^^v^^#^^v v                #          ",
    "       #            ################               #          ",
    "       #         vvvvvvvvv vv vvvvvvvvvvvv         #          ",
    "      ##       ^^^^^^^^^^^ ^^^^^^^^^^^^^^^         #          ",
    "     #^##^^^^^^^^^^^#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv##v        ",
};

/* static per-location backgrounds (used outside cutscenes) */
static const ArtBlock *const glitch[9] = {
    &art_glitch_1,
    &art_glitch_2,
    &art_glitch_3,
    &art_glitch_4,
    &art_glitch_5,
    &art_glitch_6,
    &art_glitch_7,
    &art_glitch_8,
    &art_glitch_9,
};

static const ArtBlock *const opening_cutsceen[30] = {
    &art_opening_cutsceen_1,
    &art_opening_cutsceen_2,
    &art_opening_cutsceen_3,
    &art_opening_cutsceen_4,
    &art_opening_cutsceen_5,
    &art_opening_cutsceen_6,
    &art_opening_cutsceen_7,
    &art_opening_cutsceen_8,
    &art_opening_cutsceen_9,
    &art_opening_cutsceen_10,
    &art_opening_cutsceen_11,
    &art_opening_cutsceen_12,
    &art_opening_cutsceen_13,
    &art_opening_cutsceen_14,
    &art_opening_cutsceen_15,
    &art_opening_cutsceen_16,
    &art_opening_cutsceen_17,
    &art_opening_cutsceen_18,
    &art_opening_cutsceen_19,
    &art_opening_cutsceen_20,
    &art_opening_cutsceen_21,
    &art_opening_cutsceen_22,
    &art_opening_cutsceen_23,
    &art_opening_cutsceen_24,
    &art_opening_cutsceen_25,
    &art_opening_cutsceen_26,
    &art_opening_cutsceen_27,
    &art_opening_cutsceen_28,
    &art_opening_cutsceen_29,
    &art_opening_cutsceen_30,
};

static const ArtBlock *const H_look_for_food_img[5] = {
    &art_H_look_for_food1,
    &art_H_look_for_food2,
    &art_H_look_for_food3,
    &art_H_look_for_food4,
    &art_H_look_for_food5,
};

static const ArtBlock *const H_search_your_kitchen_img[3] = {
    &art_H_search1,
    &art_H_search2,
    &art_H_search3,
};

static const ArtBlock *const H_watch_tv_img[4] = {
    &art_H_tv1,
    &art_H_tv2,
    &art_H_tv3,
    &art_H_tv4,
};

static const ArtBlock *const H_fall_asleep_img[6] = {
    &art_H_lay_down1,
    &art_H_lay_down2,
    &art_H_lay_down3,
    &art_H_lay_down4,
    &art_H_lay_down5,
    &art_H_lay_down6,
};

static const ArtBlock *const H_look_around_img[4] = {
    &art_H_look_around_letter1,
    &art_H_look_around_letter2,
    &art_H_look_around_letter3,
    &art_H_letter,
};


static const CutFrame startup_sequence[] = {
    FRAME(0, "-", "-", "-", 15000),
    FRAME(0, "Opening", "The_Night", "Made By MaxiBonng", 1000),
    FRAME(1, "Running simulation", "-", "Made By MaxiBonng", 1000),
    FRAME(2, "Running simulation", "December 12th", "-", 1000),
    FRAME(3, "Running simulation", "December 12th", "Case #19981112", 500),
    FRAME(4, "Loading", "-", "-", 500),
    FRAME(5, "Running", "log.py", "---------- 0%", DELAY_RANDOM),
    FRAME(5, NULL, "short_cut.py", "##-------- 20%", DELAY_RANDOM),
    FRAME(6, NULL, "save_load.py", "####------ 40%", DELAY_RANDOM),
    FRAME(6, NULL, "choice_tree.py", "######---- 60%", DELAY_RANDOM),
    FRAME(7, NULL, "story_functions.py", "#######--- 70%", DELAY_RANDOM),
    FRAME(7, "Loading", "logo.png", "#######--- 71%", DELAY_RANDOM),
    FRAME(7, NULL, "start_cut_sceen.png", "#######--- 72%", DELAY_RANDOM),
    FRAME(7, NULL, "start_screen.png", "#######--- 73%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_1.png", "#######--- 74%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_2.png", "#######--- 74%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_3.png", "#######--- 75%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_4.png", "#######--- 75%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_5.png", "#######--- 76%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_6.png", "#######--- 77%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_7.png", "#######--- 77%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_8.png", "#######--- 78%", DELAY_RANDOM),
    FRAME(7, NULL, "glitch_9.png", "#######--- 79%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_1.png", "########-- 80%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_2.png", "########-- 80%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_3.png", "########-- 80%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_4.png", "########-- 81%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_5.png", "########-- 81%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_6.png", "########-- 81%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_7.png", "########-- 82%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_8.png", "########-- 82%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_9.png", "########-- 82%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_10.png", "########-- 83%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_11.png", "########-- 83%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_12.png", "########-- 83%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_13.png", "########-- 84%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_14.png", "########-- 84%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_15.png", "########-- 84%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_16.png", "########-- 85%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_17.png", "########-- 85%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_18.png", "########-- 85%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_19.png", "########-- 86%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_20.png", "########-- 86%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_21.png", "########-- 86%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_22.png", "########-- 87%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_23.png", "########-- 87%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_24.png", "########-- 87%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_25.png", "########-- 88%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_26.png", "########-- 88%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_27.png", "########-- 88%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_28.png", "########-- 89%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_29.png", "########-- 89%", DELAY_RANDOM),
    FRAME(8, NULL, "opening_cutsceen_30.png", "########-- 89%", DELAY_RANDOM),
    FRAME(8, "Running", "The_Night.py", "#########- 90%", 400),
    FRAME(9, "Welcome", "Mr.############", "-", 1000),
    FRAME(9, "-", "-", "-", 1500),
};

static const CutFrame opening_cutsceen_list[] = {
    FRAME(0, "Opening", "Opening_cutsceen", "Loading .", 1000),
    FRAME(0, "Running", "Opening_cutsceen", "Loading ..", 1000),
    FRAME(1, NULL, NULL, "Loading ...", 500),
    FRAME(1, NULL, "Its night", "-", 500),
    FRAME(2, NULL, "Its night", NULL, 500),
    FROMTO(3, 7, 500),
    FRAME(8, NULL, "Your driving home", NULL, 500),
    FROMTO(9, 13, 500),
    FROMTO(10, 13, 500),
    FROMTO(10, 13, 500),
    FRAME(10, NULL, "You just got back from work", NULL, 500),
    FROMTO(11, 22, 500),
    FRAME(23, NULL, "-", NULL, 500),
    FROMTO(24, 29, 500),
    FRAME(30, NULL, "STARTING GAME", "HAVE FUN.", 1000),
    FRAME(0, NULL, NULL, "HAVE FUN..", 500),
    FRAME(0, NULL, NULL, "HAVE FUN...", 2000),
};

static const CutFrame H_look_for_food_cutsceen[] = {
    FRAME(1, "You look around", "-", "-", 500),
    FROMTO(2, 4, 500),
    FRAME(5, "You find a bun", "-", "-", 1000),
};

static const CutFrame H_search_your_kitchen_cutsceen[] = {
    FRAME(1, "You look around", "-", "-", 2500),
    FRAME(2, "Its all empty...", "-", "-", 2500),
    FRAME(3, "You finde a knife", "Carefull you can stab people whit that", "-", 5000),
};

static const CutFrame H_watch_tv_cutseen[] = {
    FRAME(1, "You watch som tv", "-", "-", 1000),
    FRAME(2, "You are starting to become tired", "-", "-", 1000),
    FRAME(3, "-", "-", "-", 1000),
    FRAME(4, "-", "-", "-", 1000),
};

static const CutFrame H_fall_asleep_cutsceen[] = {
    FRAME(1, "You lay down", "-", "-", 1000),
    FRAME(2, "-", "-", "-", 1000),
    FRAME(3, "-", "-", "-", 1000),
    FRAME(4, "You are starting to become tired", "-", "-", 1000),
    FRAME(5, "-", "-", "-", 1000),
    FRAME(6, "-", "-", "-", 1000),
};

static const CutFrame H_look_around_cutsceen[] = {
    FRAME(1, "You look around", "-", "-", 1000),
    FRAME(2, "You find something", "-", "-", 1000),
    FRAME(3, "Its a letter", "-", "-", 1000),
    FRAME(4, "-", "-", "-", 1000),
};

static const CutFrame skip_sequence[] = {
    FRAME(0, "skipping cutsceen", "-", "it not like i use a lot of time making them", 1500),
    FRAME(0, "skipping cutsceen", "-", "asshole", 500),
};

/* ---------------------------------------------------------------------
 * save_load.py port -- same save.tns / player.tnp text formats, so saves
 * made by the Python version keep working.
 *
 * save.tns layout (4 lines):
 *   line1: "<chapter>:<state>"
 *   line2: "item:[<idx>,<idx>,...]"
 *   line3: "plot:[<idx>,<idx>,...]"
 *   line4: "all:<ch>/(<state>,<state>).<ch>/(<state>,...)..."
 *
 * Note: save_load.py's load(call) had a "game_load" branch that is never
 * actually invoked anywhere in the project (grepped -- only "choice_tree"
 * is ever passed) so it's dead code and isn't ported.
 * ------------------------------------------------------------------- */
#define MAX_VISITED_CHAPTERS 8
#define MAX_VISITED_STATES 64
#define MAX_STATE_LEN 32

typedef struct {
    int chapter;
    char states[MAX_VISITED_STATES][MAX_STATE_LEN];
    int count;
} VisitedChapter;

static VisitedChapter g_visited[MAX_VISITED_CHAPTERS];
static int g_visited_count = 0;

static int g_sl_tree_chapter = 0;
static char g_sl_tree_state[MAX_STATE_LEN] = "";

static const char *no_load_state[] = {
    "running", "quit", "settings", "screen", "credits", "music", "choice", "skip"
};
#define NO_LOAD_STATE_COUNT (int)(sizeof(no_load_state) / sizeof(no_load_state[0]))

/* Reads the 4 lines of save.tns into caller-supplied buffers, each of
 * which must be SL_LINE_BUF bytes. Returns false if the file couldn't be
 * opened. */
#define SL_LINE_BUF 2048
static bool sl_read_raw(char *line1, char *line2, char *line3, char *line4) {
    FILE *f = fopen(SAVE_FILE, "r");
    if (!f) return false;
    if (!fgets(line1, SL_LINE_BUF, f)) line1[0] = '\0';
    if (!fgets(line2, SL_LINE_BUF, f)) line2[0] = '\0';
    if (!fgets(line3, SL_LINE_BUF, f)) line3[0] = '\0';
    if (!fgets(line4, SL_LINE_BUF, f)) line4[0] = '\0';
    fclose(f);
    /* strip trailing newlines, mirroring Python's .strip() */
    char *lines[4] = { line1, line2, line3, line4 };
    for (int i = 0; i < 4; i++) {
        size_t n = strlen(lines[i]);
        while (n > 0 && (lines[i][n - 1] == '\n' || lines[i][n - 1] == '\r' || lines[i][n - 1] == ' ')) {
            lines[i][--n] = '\0';
        }
    }
    return true;
}

static VisitedChapter *visited_get(int chapter, bool create) {
    for (int i = 0; i < g_visited_count; i++) {
        if (g_visited[i].chapter == chapter) return &g_visited[i];
    }
    if (create && g_visited_count < MAX_VISITED_CHAPTERS) {
        VisitedChapter *vc = &g_visited[g_visited_count++];
        vc->chapter = chapter;
        vc->count = 0;
        return vc;
    }
    return NULL;
}

static void visited_add_state(int chapter, const char *state) {
    VisitedChapter *vc = visited_get(chapter, true);
    if (!vc) return;
    for (int i = 0; i < vc->count; i++)
        if (strcmp(vc->states[i], state) == 0) return; /* already present */
    if (vc->count < MAX_VISITED_STATES) {
        strncpy(vc->states[vc->count], state, MAX_STATE_LEN - 1);
        vc->states[vc->count][MAX_STATE_LEN - 1] = '\0';
        vc->count++;
    }
}

/* Parses the "all:<ch>/(<state>,<state>).<ch>/(...)..." line into g_visited. */
static void parse_all_states_line(const char *line) {
    g_visited_count = 0;
    if (strncmp(line, "all:", 4) != 0) return;
    const char *raw = line + 4;

    char *copy = strdup(raw);
    char *chunk_save = NULL;
    char *chunk = strtok_r(copy, ".", &chunk_save);
    while (chunk) {
        char *slash = strchr(chunk, '/');
        if (slash) {
            *slash = '\0';
            int ch = atoi(chunk);
            const char *states_raw = slash + 1;
            /* strip surrounding parens */
            char statesbuf[1024];
            strncpy(statesbuf, states_raw, sizeof statesbuf - 1);
            statesbuf[sizeof statesbuf - 1] = '\0';
            size_t n = strlen(statesbuf);
            if (n > 0 && statesbuf[n - 1] == ')') statesbuf[n - 1] = '\0';
            char *s = statesbuf;
            if (*s == '(') s++;

            VisitedChapter *vc = visited_get(ch, true);
            if (vc) {
                char *state_save = NULL;
                char *state_tok = strtok_r(s, ",", &state_save);
                while (state_tok && vc->count < MAX_VISITED_STATES) {
                    strncpy(vc->states[vc->count], state_tok, MAX_STATE_LEN - 1);
                    vc->states[vc->count][MAX_STATE_LEN - 1] = '\0';
                    vc->count++;
                    state_tok = strtok_r(NULL, ",", &state_save);
                }
            }
        }
        chunk = strtok_r(NULL, ".", &chunk_save);
    }
    free(copy);
}

/* choice_tree.py's tree.load() calls sl.load("choice_tree") -- this is
 * that path. Populates g_visited / g_sl_tree_chapter / g_sl_tree_state. */
static void sl_load_choice_tree(void) {
    char l1[SL_LINE_BUF], l2[SL_LINE_BUF], l3[SL_LINE_BUF], l4[SL_LINE_BUF];
    if (!sl_read_raw(l1, l2, l3, l4)) return;

    char *colon = strchr(l1, ':');
    if (colon) {
        *colon = '\0';
        g_sl_tree_chapter = atoi(l1);
        strncpy(g_sl_tree_state, colon + 1, sizeof g_sl_tree_state - 1);
        g_sl_tree_state[sizeof g_sl_tree_state - 1] = '\0';
    }

    parse_all_states_line(l4);
}

static int sl_get_max_chapter(void) {
    char l1[SL_LINE_BUF], l2[SL_LINE_BUF], l3[SL_LINE_BUF], l4[SL_LINE_BUF];
    if (!sl_read_raw(l1, l2, l3, l4)) return 0;
    if (strncmp(l4, "all:", 4) != 0) return 0;

    int max_ch = 0;
    bool any = false;
    char *copy = strdup(l4 + 4);
    char *chunk_save = NULL;
    char *chunk = strtok_r(copy, ".", &chunk_save);
    while (chunk) {
        char *slash = strchr(chunk, '/');
        if (slash) {
            *slash = '\0';
            int ch = atoi(chunk);
            if (!any || ch > max_ch) { max_ch = ch; any = true; }
        }
        chunk = strtok_r(NULL, ".", &chunk_save);
    }
    free(copy);
    return max_ch;
}

static bool state_is_no_load(const char *state) {
    for (int i = 0; i < NO_LOAD_STATE_COUNT; i++)
        if (strcmp(no_load_state[i], state) == 0) return true;
    return false;
}

static void sl_save(int chapter, const char *state) {
    if (state_is_no_load(state)) return;

    char l1[SL_LINE_BUF], l2[SL_LINE_BUF], l3[SL_LINE_BUF], l4[SL_LINE_BUF];
    if (!sl_read_raw(l1, l2, l3, l4)) {
        l1[0] = l2[0] = l3[0] = '\0';
        strcpy(l4, "");
    }

    char chapter_line[64];
    snprintf(chapter_line, sizeof chapter_line, "%d:%s", chapter, state);

    char item_line[128] = "item:[";
    {
        bool first = true;
        for (int i = 0; i < ITEM_COUNT; i++) {
            if (item_list[i].happened) {
                char idxbuf[16];
                snprintf(idxbuf, sizeof idxbuf, "%s%d", first ? "" : ", ", i);
                strncat(item_line, idxbuf, sizeof item_line - strlen(item_line) - 1);
                first = false;
            }
        }
        strncat(item_line, "]", sizeof item_line - strlen(item_line) - 1);
    }

    char plot_line[128] = "plot:[";
    {
        bool first = true;
        for (int i = 0; i < PLOT_COUNT; i++) {
            if (plot_list[i].happened) {
                char idxbuf[16];
                snprintf(idxbuf, sizeof idxbuf, "%s%d", first ? "" : ", ", i);
                strncat(plot_line, idxbuf, sizeof plot_line - strlen(plot_line) - 1);
                first = false;
            }
        }
        strncat(plot_line, "]", sizeof plot_line - strlen(plot_line) - 1);
    }

    /* re-parse existing "all:" line, then add the current (chapter,state) */
    parse_all_states_line(l4);
    visited_add_state(chapter, state);

    char all_line[2048] = "all:";
    for (int i = 0; i < g_visited_count; i++) {
        char part[1200];
        int off = snprintf(part, sizeof part, "%s%d/(", i == 0 ? "" : ".", g_visited[i].chapter);
        for (int j = 0; j < g_visited[i].count; j++) {
            off += snprintf(part + off, sizeof part - off, "%s%s", j == 0 ? "" : ",", g_visited[i].states[j]);
        }
        snprintf(part + off, sizeof part - off, ")");
        strncat(all_line, part, sizeof all_line - strlen(all_line) - 1);
    }

    FILE *f = fopen(SAVE_FILE, "w");
    if (!f) return;
    fprintf(f, "%s\n%s\n%s\n%s\n", chapter_line, item_line, plot_line, all_line);
    fclose(f);
}

/* player.tnp layout (3 lines):
 *   line1: "<music_volume>:<soundfx_volume>"
 *   line2: "<ON|OFF>"              (shader_on setting; kept for save
 *                                    compatibility, but is a display-only
 *                                    no-op here since there's no shader)
 *   line3: "<scale>" or "fullscreen" (kept as a cosmetic settings value;
 *                                      there's no real window to resize
 *                                      in a terminal)
 */
static char g_shader_on[8] = "ON";
static float g_scale = 3.0f;
static bool g_fullscreen = false;

static void sl_load_settings(void) {
    FILE *f = fopen(SETTINGS_FILE, "r");
    if (!f) return;
    char l1[64] = "", l2[64] = "", l3[64] = "";
    if (!fgets(l1, sizeof l1, f)) l1[0] = '\0';
    if (!fgets(l2, sizeof l2, f)) l2[0] = '\0';
    if (!fgets(l3, sizeof l3, f)) l3[0] = '\0';
    fclose(f);

    int musicvolume = 100, soundfxvolume = 100;
    char *colon = strchr(l1, ':');
    if (colon) {
        *colon = '\0';
        musicvolume = atoi(l1);
        soundfxvolume = atoi(colon + 1);
    }

    size_t n = strlen(l2);
    while (n > 0 && (l2[n - 1] == '\n' || l2[n - 1] == '\r')) l2[--n] = '\0';
    strncpy(g_shader_on, l2, sizeof g_shader_on - 1);

    n = strlen(l3);
    while (n > 0 && (l3[n - 1] == '\n' || l3[n - 1] == '\r' || l3[n - 1] == ' ')) l3[--n] = '\0';
    if (strcmp(l3, "fullscreen") == 0) {
        g_scale = 3.0f;
        g_fullscreen = true;
    } else if (l3[0]) {
        g_scale = strtof(l3, NULL);
    }

    music_set_volume(musicvolume);
    soundfx_set_volume(soundfxvolume);
}

static void sl_save_settings(void) {
    char scale_line[32];
    if (g_fullscreen) {
        snprintf(scale_line, sizeof scale_line, "fullscreen");
    } else {
        snprintf(scale_line, sizeof scale_line, "%g", g_scale);
    }
    FILE *f = fopen(SETTINGS_FILE, "w");
    if (!f) return;
    fprintf(f, "%d:%d\n%s\n%s\n", g_music.volume, g_soundfx_volume, g_shader_on, scale_line);
    fclose(f);
}

/* ---------------------------------------------------------------------
 * choice_tree.py port
 * ------------------------------------------------------------------- */
#define MAX_BOXES 32
#define MAX_ARROWS 8
#define MAX_CHAPTERS_TREE 8

typedef struct {
    int x, y;              /* box_location, e.g. "0:0" */
    char box_type[16];     /* "normal" / "cutsceen" / "next" */
    char hint[128];        /* stored for fidelity; never rendered in the
                               original either -- short_cut.choice()'s
                               "Hint: " text never actually appends it */
    int arrow_to[MAX_ARROWS][2];
    int arrow_count;
    char box_state[MAX_STATE_LEN];
    /* move_to[0..3] = up,left,down,right; x=-999 means "None" (blocked) */
    int move_to[4][2];
} TreeBox;

typedef struct {
    int chapter_value;
    TreeBox boxes[MAX_BOXES];
    int box_count;
} TreeChapter;

static TreeChapter g_tree_chapters[MAX_CHAPTERS_TREE];
static int g_tree_chapter_count = 0;

static bool g_tree_move_selected = false;
static bool g_tree_is_load = false;
static bool g_tree_on_chapter = true;
static int g_tree_chapter_load = 0;
static int g_tree_x = 0, g_tree_y = 0; /* "place": the pan/camera offset */

#define TREE_NONE -999

static void parse_xy(const char *s, int *x, int *y) {
    if (strcmp(s, "None") == 0) { *x = TREE_NONE; *y = TREE_NONE; return; }
    sscanf(s, "%d:%d", x, y);
}

/* Parses choice_tree.json once at startup into g_tree_chapters. */
static void tree_json_load(void) {
    char *text = read_whole_file(TREE_JSON_FILE);
    if (!text) return;
    JValue *root = json_parse(text);
    JValue *chapters = j_get(root, "chapters");
    int chcount = j_arr_count(chapters);
    if (chcount > MAX_CHAPTERS_TREE) chcount = MAX_CHAPTERS_TREE;

    for (int ci = 0; ci < chcount; ci++) {
        JValue *chobj = j_index(chapters, ci);
        TreeChapter *tc = &g_tree_chapters[ci];
        JValue *chval = j_get(chobj, "chapter_value");
        tc->chapter_value = chval ? (int)chval->num : ci;

        JValue *box_list = j_get(chobj, "box_list");
        int bcount = j_arr_count(box_list);
        if (bcount > MAX_BOXES) bcount = MAX_BOXES;
        tc->box_count = bcount;

        for (int bi = 0; bi < bcount; bi++) {
            JValue *bobj = j_index(box_list, bi);
            TreeBox *box = &tc->boxes[bi];

            parse_xy(j_str(j_get(bobj, "box_location")), &box->x, &box->y);
            strncpy(box->box_type, j_str(j_get(bobj, "box_type")), sizeof box->box_type - 1);
            strncpy(box->hint, j_str(j_get(bobj, "box_hint")), sizeof box->hint - 1);
            strncpy(box->box_state, j_str(j_get(bobj, "box_state")), sizeof box->box_state - 1);

            JValue *arrows = j_get(bobj, "arrow_to_boxs");
            int acount = j_arr_count(arrows);
            if (acount > MAX_ARROWS) acount = MAX_ARROWS;
            box->arrow_count = acount;
            for (int ai = 0; ai < acount; ai++) {
                parse_xy(j_str(j_index(arrows, ai)), &box->arrow_to[ai][0], &box->arrow_to[ai][1]);
            }

            JValue *move_to = j_get(bobj, "move_to");
            for (int mi = 0; mi < 4; mi++) {
                parse_xy(j_str(j_index(move_to, mi)), &box->move_to[mi][0], &box->move_to[mi][1]);
            }
        }
    }
    g_tree_chapter_count = chcount;
    free(text);
}

/* choice_tree.py's move(): the current codebase's version of this
 * function iterates over a bogus move_index (indexing into the box's own
 * move_to array by "how many boxes we've scanned so far", then iterating
 * over the *characters* of the resulting string) and crashes with an
 * unhandled exception on nearly every input -- confirmed by running it in
 * isolation against choice_tree.json. Per direction, this ports the
 * clearly-intended behavior instead: look up the matched box's own
 * move_to entry directly. The direction->index convention itself
 * (0=up,1=left,2=down,3=right) is unchanged and intentional. */
static void tree_move(const char *direction) {
    if (g_tree_chapter_load < 0 || g_tree_chapter_load >= g_tree_chapter_count) return;
    TreeChapter *tc = &g_tree_chapters[g_tree_chapter_load];

    for (int i = 0; i < tc->box_count; i++) {
        TreeBox *box = &tc->boxes[i];
        if (box->x == g_tree_x && box->y == g_tree_y) {
            int idx;
            if (strcmp(direction, "up") == 0) idx = 0;
            else if (strcmp(direction, "left") == 0) idx = 1;
            else if (strcmp(direction, "down") == 0) idx = 2;
            else if (strcmp(direction, "right") == 0) idx = 3;
            else return;

            if (box->move_to[idx][0] != TREE_NONE) {
                g_tree_x = box->move_to[idx][0];
                g_tree_y = box->move_to[idx][1];
            }
            return;
        }
    }
}

static bool tree_state_visited(int chapter, const char *state) {
    for (int i = 0; i < g_visited_count; i++) {
        if (g_visited[i].chapter != chapter) continue;
        for (int j = 0; j < g_visited[i].count; j++)
            if (strcmp(g_visited[i].states[j], state) == 0) return true;
        return false;
    }
    return false;
}

/* ASCII replacement for choice_tree.py's draw(): renders the visited
 * subset of the current chapter's box graph into the main panel, using
 * the same "middel + (box_size+margin)*(coord-pan)" placement idea as
 * the pygame version, just in character cells instead of pixels. Only
 * visited boxes are drawn (fog of war), matching the original -- but
 * arrows from a visited box reach out to *all* of its listed neighbors,
 * visited or not, same as before. */
static void tree_draw_main_area(void) {
    if (g_tree_chapter_load < 0 || g_tree_chapter_load >= g_tree_chapter_count) return;
    TreeChapter *tc = &g_tree_chapters[g_tree_chapter_load];

    const int cell_w = 9, cell_h = 3;
    const int origin_row = g_main_top + MAIN_H / 2;
    const int origin_col = g_main_left + UI_WIDTH / 2;
    const int min_row = g_main_top, max_row = g_main_top + MAIN_H - 1;
    const int min_col = g_main_left, max_col = g_main_left + UI_WIDTH - 1;

    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));

    for (int i = 0; i < tc->box_count; i++) {
        TreeBox *box = &tc->boxes[i];
        if (!tree_state_visited(g_tree_chapter_load, box->box_state)) continue;

        int brow = origin_row + (box->y - g_tree_y) * cell_h;
        int bcol = origin_col + (box->x - g_tree_x) * cell_w;

        /* arrows: L-shaped connector (horizontal at source row, then
         * vertical to the target row), matching pygame.draw.lines with
         * points (from,from)-(to,from)-(to,to). */
        for (int a = 0; a < box->arrow_count; a++) {
            int trow = origin_row + (box->arrow_to[a][1] - g_tree_y) * cell_h;
            int tcol = origin_col + (box->arrow_to[a][0] - g_tree_x) * cell_w;

            int c0 = brow < min_row || brow > max_row ? -1 : brow;
            if (c0 >= 0) {
                int lo = bcol < tcol ? bcol : tcol, hi = bcol < tcol ? tcol : bcol;
                for (int c = lo; c <= hi; c++) {
                    if (c < min_col || c > max_col) continue;
                    mvaddch(c0, c, '-');
                }
            }
            if (tcol >= min_col && tcol <= max_col) {
                int lo = brow < trow ? brow : trow, hi = brow < trow ? trow : brow;
                for (int r = lo; r <= hi; r++) {
                    if (r < min_row || r > max_row) continue;
                    mvaddch(r, tcol, '|');
                }
            }
            if (c0 >= 0 && tcol >= min_col && tcol <= max_col) mvaddch(c0, tcol, '+');
        }

        if (brow >= min_row && brow <= max_row && bcol - 1 >= min_col && bcol + 1 <= max_col) {
            const char *glyph = "[ ]";
            if (strcmp(box->box_type, "cutsceen") == 0) glyph = "( )";
            else if (strcmp(box->box_type, "next") == 0) glyph = "<*>";
            mvprintw(brow, bcol - 1, "%s", glyph);
        }
    }

    /* player/camera marker, drawn last so it's on top -- same z-order as
     * the red dot in the original draw(). */
    attroff(COLOR_PAIR(COLOR_PAIR_NORMAL));
    attron(COLOR_PAIR(COLOR_PAIR_MARKER) | A_BOLD);
    mvaddch(origin_row, origin_col, '@');
    attroff(COLOR_PAIR(COLOR_PAIR_MARKER) | A_BOLD);
}

static void tree_load(void) {
    sl_load_choice_tree();

    if (g_tree_on_chapter) {
        for (int i = 0; i < g_tree_chapter_count; i++) {
            if (g_sl_tree_chapter == g_tree_chapters[i].chapter_value) {
                g_tree_chapter_load = g_tree_chapters[i].chapter_value;
            }
        }
    }
    g_tree_on_chapter = true;

    /* Python indexes data["chapters"][chapter_load] positionally, not by
     * chapter_value -- same here, with a bounds clamp to avoid a crash
     * (the original would raise IndexError; a C port needs to not
     * segfault instead). */
    if (g_tree_chapter_load < 0) g_tree_chapter_load = 0;
    if (g_tree_chapter_load >= g_tree_chapter_count) g_tree_chapter_load = g_tree_chapter_count - 1;

    g_tree_is_load = true;
    tree_draw_main_area();
}

/* ---------------------------------------------------------------------
 * story_functions.py port: state machine core (redraw, choice handling,
 * cutscene player). short_cut.py's screen functions are defined further
 * below and referenced here via forward declarations, same as the
 * mutual references between story_functions.py/short_cut.py in Python.
 * ------------------------------------------------------------------- */
typedef void (*CutFn)(void);

static char g_state[MAX_STATE_LEN] = "running";
static int g_chapter = 0;
static int g_valg = 1;
static bool g_selected_valg[5]; /* 1..4 used, [0] unused */
static bool g_allow_input = true;

static bool g_skip_cutsceen = false;
static char g_skip_target_state[MAX_STATE_LEN] = "";
static CutFn g_skip_target_cut = NULL;

static long g_cutsceen_index = 0;
static long long g_cutsceen_next_time = 0;
static int g_cutsceen_img_index = 0;

typedef enum { ART_NONE, ART_FILL, ART_IMAGE } ArtKind;
static ArtKind g_cut_art_kind = ART_NONE;
static const ArtBlock *g_cut_art = NULL;

static char g_prev_story[3][128] = { "-", "-", "-" };
static char g_cur_story[3][128] = { "-", "-", "-" };
static char g_cur_valg[4][64] = { "-", "-", "-", "-" };

/* forward declarations for short_cut.py equivalents (defined later) */
static void cut_menu(void);
static void cut_settings(void);
static void cut_music(void);
static void cut_credits(void);
static void cut_screen(void);
static void cut_choice(void);
static void cut_H_continue(void);
static void cut_H_kitchen(void);
static void cut_H_livingroom(void);
static void cut_H_room(void);
static void cut_H_look_around(void);
static void cut_H_lay_down(void);
static void cut_H_sit_down(void);

static void redraw(void);

static void story_update(const char *t1, const char *t2, const char *t3) {
    if (t1) { strncpy(g_prev_story[0], t1, sizeof g_prev_story[0] - 1); g_prev_story[0][sizeof g_prev_story[0]-1]='\0'; }
    if (t2) { strncpy(g_prev_story[1], t2, sizeof g_prev_story[1] - 1); g_prev_story[1][sizeof g_prev_story[1]-1]='\0'; }
    if (t3) { strncpy(g_prev_story[2], t3, sizeof g_prev_story[2] - 1); g_prev_story[2][sizeof g_prev_story[2]-1]='\0'; }
    memcpy(g_cur_story[0], g_prev_story[0], sizeof g_cur_story[0]);
    memcpy(g_cur_story[1], g_prev_story[1], sizeof g_cur_story[1]);
    memcpy(g_cur_story[2], g_prev_story[2], sizeof g_cur_story[2]);
}

static void valg_update(const char *v1, const char *v2, const char *v3, const char *v4) {
    strncpy(g_cur_valg[0], v1, sizeof g_cur_valg[0] - 1); g_cur_valg[0][sizeof g_cur_valg[0]-1]='\0';
    strncpy(g_cur_valg[1], v2, sizeof g_cur_valg[1] - 1); g_cur_valg[1][sizeof g_cur_valg[1]-1]='\0';
    strncpy(g_cur_valg[2], v3, sizeof g_cur_valg[2] - 1); g_cur_valg[2][sizeof g_cur_valg[2]-1]='\0';
    strncpy(g_cur_valg[3], v4, sizeof g_cur_valg[3] - 1); g_cur_valg[3][sizeof g_cur_valg[3]-1]='\0';
}

static void choice_select(const char *s1, CutFn c1, const char *s2, CutFn c2,
                           const char *s3, CutFn c3, const char *s4, CutFn c4) {
    if (g_selected_valg[1]) {
        if (s1) strncpy(g_state, s1, sizeof g_state - 1);
        if (c1) c1();
        g_selected_valg[1] = false;
    } else if (g_selected_valg[2]) {
        if (s2) strncpy(g_state, s2, sizeof g_state - 1);
        if (c2) c2();
        g_selected_valg[2] = false;
    } else if (g_selected_valg[3]) {
        if (s3) strncpy(g_state, s3, sizeof g_state - 1);
        if (c3) c3();
        g_selected_valg[3] = false;
    } else if (g_selected_valg[4]) {
        if (s4) strncpy(g_state, s4, sizeof g_state - 1);
        if (c4) c4();
        g_selected_valg[4] = false;
    }
}

static void text_valg(void) {
    if (g_valg >= 1 && g_valg <= 4) g_selected_valg[g_valg] = true;
}

/* Fallback text shown in the main panel on states with no associated art
 * (e.g. Music/Credits, which had no background image in the original
 * either -- image_make() never loaded anything for them). */
static const char *scene_label(void) {
    if (strcmp(g_state, "music") == 0) return "[ MUSIC ]";
    if (strcmp(g_state, "H_continue") == 0) return "[ HOME ]";
    return "";
}

/* Static per-location background art, matching story_functions.py's
 * redraw() image-blit dispatch (image_make()'s start_front/kitchen_k/
 * kitchen_uk/livingroom/sit_down/room/lay_down). Returns NULL for states
 * with no art (falls back to scene_label()). */
static const ArtBlock *scene_art(void) {
    if (strcmp(g_state, "menu") == 0 || strcmp(g_state, "settings") == 0 || strcmp(g_state, "screen") == 0)
        return &art_start_screen;
    if (strcmp(g_state, "H_kitchen") == 0)
        return get_plot("item", "knife") ? &art_kitchen_uk : &art_kitchen_k;
    if (strcmp(g_state, "H_livingroom") == 0) return &art_livingroom;
    if (strcmp(g_state, "H_sit_down") == 0) return &art_sit_down;
    if (strcmp(g_state, "H_room") == 0) return &art_room;
    if (strcmp(g_state, "H_lay_down") == 0) return &art_lay_down_static;
    return NULL;
}

static void draw_centered(int row, int left, int width, const char *text) {
    int len = (int)strlen(text);
    int col = left + (width - len) / 2;
    if (col < left) col = left;
    mvprintw(row, col, "%.*s", width, text);
}

/* Renders one converted image into the main panel using half-block
 * glyphs -- see the ArtBlock typedef for the 4-symbol encoding. */
static void draw_art(const ArtBlock art, int top, int left) {
    for (int r = 0; r < MAIN_H; r++) {
        const char *row = art[r];
        for (int c = 0; c < UI_WIDTH; c++) {
            switch (row[c]) {
                case '#':
                    attron(COLOR_PAIR(COLOR_PAIR_INV));
                    mvaddch(top + r, left + c, ' ');
                    attroff(COLOR_PAIR(COLOR_PAIR_INV));
                    break;
                case '^':
                    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));
                    mvaddstr(top + r, left + c, "▀"); /* upper half block */
                    break;
                case 'v':
                    attron(COLOR_PAIR(COLOR_PAIR_INV));
                    mvaddstr(top + r, left + c, "▀"); /* fg=black,bg=green -> looks lower-filled */
                    attroff(COLOR_PAIR(COLOR_PAIR_INV));
                    break;
                default:
                    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));
                    mvaddch(top + r, left + c, ' ');
                    break;
            }
        }
    }
    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));
}

/* Solid green fill, matching cutsceen()'s `main_canvas.fill(green)` for
 * img_index==0 frames. */
static void draw_art_fill_green(int top, int left) {
    attron(COLOR_PAIR(COLOR_PAIR_INV));
    for (int r = 0; r < MAIN_H; r++) {
        mvprintw(top + r, left, "%*s", UI_WIDTH, "");
    }
    attroff(COLOR_PAIR(COLOR_PAIR_INV));
    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));
}

static void redraw(void) {
    const char *valg_log = (g_valg >= 1 && g_valg <= 4) ? g_cur_valg[g_valg - 1] : "";
    log_write(g_state, g_valg, valg_log);

    /* menu/settings/screen persist settings to disk every redraw, same
     * as story_functions.py's redraw() */
    if (strcmp(g_state, "menu") == 0 || strcmp(g_state, "settings") == 0 || strcmp(g_state, "screen") == 0) {
        sl_save_settings();
    }

    /* background music selection (text-only: just tracks which "track"
     * would be playing, for the Music menu display) */
    if (strcmp(g_state, "running") == 0) {
        if (!music_current() || strcmp(music_current(), "start_up") != 0) music_switch("start_up");
    } else if (strcmp(g_state, "menu") == 0 || strcmp(g_state, "settings") == 0 ||
               strcmp(g_state, "screen") == 0 || strcmp(g_state, "credits") == 0 ||
               strcmp(g_state, "choice") == 0 || strcmp(g_state, "opening_cutsceen") == 0) {
        if (strcmp(music_current(), "night") != 0) music_switch("night");
    } else if (strncmp(g_state, "H", 1) == 0) {
        if (strcmp(music_current(), "home") != 0) music_switch("home");
    }

    sl_save(g_chapter, g_state);

    /* ---- draw ---- */
    erase();
    attron(COLOR_PAIR(COLOR_PAIR_NORMAL));

    int box_w = UI_WIDTH + 2;
    int box_h = MAIN_H + 1 + STORY_H + 1 + CHOICE_H + 2;
    int by = g_box_top, bx = g_box_left;
    for (int c = 0; c < box_w; c++) { mvaddch(by, bx + c, '-'); mvaddch(by + box_h - 1, bx + c, '-'); }
    for (int r = 0; r < box_h; r++) { mvaddch(by + r, bx, '|'); mvaddch(by + r, bx + box_w - 1, '|'); }
    mvaddch(by, bx, '+'); mvaddch(by, bx + box_w - 1, '+');
    mvaddch(by + box_h - 1, bx, '+'); mvaddch(by + box_h - 1, bx + box_w - 1, '+');
    int div1 = g_main_top + MAIN_H;
    int div2 = g_story_top + STORY_H;
    for (int c = 0; c < UI_WIDTH; c++) { mvaddch(div1, g_main_left + c, '-'); mvaddch(div2, g_story_left + c, '-'); }

    /* main panel */
    if (strcmp(g_state, "choice") == 0) {
        tree_draw_main_area();
    } else if (!g_allow_input) {
        if (g_cut_art_kind == ART_IMAGE) draw_art(*g_cut_art, g_main_top, g_main_left);
        else if (g_cut_art_kind == ART_FILL) draw_art_fill_green(g_main_top, g_main_left);
        else draw_centered(g_main_top + MAIN_H / 2, g_main_left, UI_WIDTH, "( cutscene playing... press S to skip )");
    } else {
        const ArtBlock *art = scene_art();
        if (art) draw_art(*art, g_main_top, g_main_left);
        else draw_centered(g_main_top + MAIN_H / 2, g_main_left, UI_WIDTH, scene_label());
    }

    /* story panel */
    for (int i = 0; i < 3; i++) {
        mvprintw(g_story_top + i, g_story_left, "%-*.*s", UI_WIDTH, UI_WIDTH, g_cur_story[i]);
    }

    /* choice panel */
    if (!g_allow_input) {
        attron(A_REVERSE);
        for (int i = 0; i < CHOICE_H; i++) mvprintw(g_choice_top + i, g_choice_left, "%*s", UI_WIDTH, "");
        attroff(A_REVERSE);
    } else {
        for (int i = 0; i < CHOICE_H; i++) {
            bool sel = (g_valg == i + 1);
            if (sel) attron(A_REVERSE);
            mvprintw(g_choice_top + i, g_choice_left, "%d: %-*.*s", i + 1, UI_WIDTH - 3, UI_WIDTH - 3, g_cur_valg[i]);
            if (sel) attroff(A_REVERSE);
        }
    }

    attroff(COLOR_PAIR(COLOR_PAIR_NORMAL));
    refresh();
}

/* story_functions.py's cutsceen(): advances at most one step per call,
 * driven by the main loop tick, same non-blocking pacing as the original
 * (so "press S to skip" stays responsive mid-cutscene). */
static void sf_cutsceen(const CutFrame *frames, int count, const ArtBlock *const *img_list,
                         const char *state_to, CutFn cut_to) {
    g_allow_input = false;

    if (g_skip_cutsceen) {
        g_cutsceen_index = 0;
        g_cutsceen_next_time = 0;
        g_cutsceen_img_index = 0;
        g_skip_cutsceen = false;
        strncpy(g_skip_target_state, state_to, sizeof g_skip_target_state - 1);
        g_skip_target_cut = cut_to;
        strncpy(g_state, "skip", sizeof g_state - 1);
        redraw();
        return;
    }

    long long now = now_ms();

    if (g_cutsceen_index < count) {
        if (now >= g_cutsceen_next_time) {
            const CutFrame *f = &frames[g_cutsceen_index];
            int delay_ms = 0;

            if (f->type == FR_FRAME) {
                if (f->delay_ms == DELAY_RANDOM) {
                    /* matches the original: "random" delay is only ever
                       used while state=="running" (the startup sequence) */
                    delay_ms = 50 + rand() % 101;
                } else {
                    delay_ms = f->delay_ms;
                }
                if (f->img_from == 0) {
                    g_cut_art_kind = ART_FILL;
                } else {
                    g_cut_art_kind = ART_IMAGE;
                    g_cut_art = img_list[f->img_from - 1];
                }
                story_update(f->text1, f->text2, f->text3);
                redraw();
            } else { /* FR_FROM_TO */
                int current_img = f->img_from + g_cutsceen_img_index;
                delay_ms = f->delay_ms;
                g_cut_art_kind = ART_IMAGE;
                g_cut_art = img_list[current_img - 1];
                story_update(NULL, NULL, NULL);
                redraw();
                if (current_img < f->img_to) {
                    g_cutsceen_img_index++;
                    g_cutsceen_next_time = now + delay_ms;
                    return;
                } else {
                    g_cutsceen_img_index = 0;
                }
            }
            g_cutsceen_next_time = now + delay_ms;
            g_cutsceen_index++;
        }
    } else {
        if (now >= g_cutsceen_next_time) {
            g_cutsceen_index = 0;
            g_cutsceen_next_time = 0;
            g_cutsceen_img_index = 0;
            g_allow_input = true;
            strncpy(g_state, state_to, sizeof g_state - 1);
            if (cut_to) cut_to();
            redraw();
        }
    }
}

/* ---------------------------------------------------------------------
 * short_cut.py port
 * ------------------------------------------------------------------- */
#define SCREEN_W 320
#define SCREEN_H 240 /* cosmetic only -- kept so the Screen menu's "the
                        screen is WxH" text still reads sensibly */

static void cut_menu(void) {
    story_update("Welcome to The Night", "Case #19981112", "you can always press M to return to the main menu");
    valg_update("Continue", "Settings", "Choice Tree - saves", "Quit");
}

static void cut_settings(void) {
    story_update("Settings", "-", "-");
    valg_update("screen", "music", "credits", "back");
}

static void cut_music(void) {
    char line2[64];
    snprintf(line2, sizeof line2, "Curently playing: %s ", music_current());
    story_update("Music", line2, "-");

    char v1[32], v2[32], v3[32];
    snprintf(v1, sizeof v1, "<- Change music ->");
    snprintf(v2, sizeof v2, "<- Volume %d ->", g_music.volume);
    snprintf(v3, sizeof v3, "<- Sound Fx %d ->", g_soundfx_volume);
    valg_update(v1, v2, v3, "back");
}

static void cut_credits(void) {
    story_update("Made by -Maxibonng", "Special thanks: -Engineer_0001   -Likvik   -ArthurR2", "-");
    valg_update("-", "-", "-", "back");
}

static void cut_screen(void) {
    if (g_valg == 1) {
        char line2[64];
        snprintf(line2, sizeof line2, "the screen is  %dx%d", (int)(SCREEN_H * g_scale), (int)(SCREEN_W * g_scale));
        story_update("The screen is fixed at a 240x320 ratio", line2, "-");
    } else if (g_valg == 2) {
        story_update("Shaders is recomend ON", "for better preformans turn OFF", "-");
    } else {
        story_update("-", "-", "-");
    }

    char v1[32], v2[32];
    snprintf(v1, sizeof v1, "<- scale = %g ->", g_scale);
    snprintf(v2, sizeof v2, "shader %s", g_shader_on);
    valg_update(v1, v2, "-", "back");
}

static void cut_choice(void) {
    int max_chapter = sl_get_max_chapter();
    char line2[64];
    snprintf(line2, sizeof line2, "Chapter unlocked 0 - %d", max_chapter);
    story_update("Here you can see your progress in from of a tree", line2, "Hint: ");

    char v2[32];
    snprintf(v2, sizeof v2, "<- chapter %d ->", g_tree_chapter_load);
    if (g_tree_move_selected) {
        valg_update("Move On", v2, "saves", "Back");
    } else {
        valg_update("Move Off", v2, "saves", "Back");
    }
}

static void cut_H_continue(void) {
    g_chapter = 1;
    story_update("You just got home", "Your tired maybe get some sleep", "-");
    valg_update("Sit down in the couch", "Go to your kitchen", "Go to your room", "-");
}

static void cut_H_kitchen(void) {
    if (get_plot("item", "knife") || get_plot("item", "bun")) {
        story_update("The kitchen", "-", "-");
        valg_update("-", "-", "Go to the living room", "-");
    } else {
        story_update("The kitchen", "You should probely eat", ":IM NOT HUNGRY");
        valg_update("Look for food", "Search your kitchen", "Go to the living room", "-");
    }
}

static void cut_H_livingroom(void) {
    story_update("Home Sweet Home", "Better then the office", "-");
    valg_update("Sit down in the couch", "Go to your kitchen", "Go to your room", "-");
}

static void cut_H_room(void) {
    if (get_plot("item", "letter")) {
        story_update("You walk into your room", "Its a bit messy", ":...");
        valg_update("Look at letter", "Lay down in your bed", "-", "Go to the living room");
    } else {
        story_update("You walk into your room", "Its a bit messy", ".");
        valg_update("Look around your room", "Lay down in your bed", "-", "Go to the living room");
    }
}

static void cut_H_look_around(void) {
    story_update("It a letter from robbert", "-", "-");
    valg_update("put letter down", "-", "-", "-");
}

static void cut_H_lay_down(void) {
    story_update("You lay in your bed", "-", "-");
    valg_update("Stand up", "Go to sleep", "-", "-");
}

static void cut_H_sit_down(void) {
    story_update("Tired?", "Maybe some TV can relax you?", "-");
    valg_update("Stand up", "Watch som TV", "-", "-");
}

/* ---------------------------------------------------------------------
 * The_night.py port: layout setup, input handling, main loop
 * ------------------------------------------------------------------- */
static void ui_layout_init(void) {
    int term_h, term_w;
    getmaxyx(stdscr, term_h, term_w);

    int box_w = UI_WIDTH + 2;
    int box_h = MAIN_H + 1 + STORY_H + 1 + CHOICE_H + 2;

    g_box_top = (term_h - box_h) / 2;
    g_box_left = (term_w - box_w) / 2;
    if (g_box_top < 0) g_box_top = 0;
    if (g_box_left < 0) g_box_left = 0;

    g_main_top = g_box_top + 1;
    g_main_left = g_box_left + 1;
    g_story_top = g_main_top + MAIN_H + 1;
    g_story_left = g_main_left;
    g_choice_top = g_story_top + STORY_H + 1;
    g_choice_left = g_main_left;
}

static void sf_setup(void) {
    sl_load_settings();
    tree_json_load();
    redraw();
    tree_load();
}

static volatile sig_atomic_t g_sigint_received = 0;
static void on_sigint(int signo) { (void)signo; g_sigint_received = 1; }

int main(void) {
    srand((unsigned int)time(NULL));
    g_start_ms = 0;
    {
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        g_start_ms = (long long)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
    }

    signal(SIGINT, on_sigint);

    setlocale(LC_ALL, ""); /* needed for the UTF-8 half-block art glyphs */
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    keypad(stdscr, TRUE);
    timeout(33); /* ~30Hz poll, same pacing as clock.tick(30) while still
                    reading input promptly (mirrors the pygame event loop) */

    start_color();
    use_default_colors();
    init_pair(COLOR_PAIR_NORMAL, COLOR_GREEN, COLOR_BLACK);
    init_pair(COLOR_PAIR_MARKER, COLOR_RED, COLOR_BLACK);
    init_pair(COLOR_PAIR_INV, COLOR_BLACK, COLOR_GREEN);

    ui_layout_init();
    sf_setup();

    bool need_redraw = true;
    bool running = true;

    while (running) {
        if (g_sigint_received) {
            log_write_close();
            running = false;
            break;
        }

        int ch = getch();
        if (ch == KEY_RESIZE) {
            ui_layout_init();
            need_redraw = true;
        } else if (ch != ERR) {
            bool is_enter = (ch == '\n' || ch == '\r' || ch == KEY_ENTER);
            bool is_space = (ch == ' ');

            /* Mirrors the original's `K_SPACE or (K_RETURN and allow_input)`
             * condition (Python `and` binds tighter than `or`): Space
             * always registers a selection even mid-cutscene, Enter only
             * when allow_input is set. This isn't just cosmetic -- the
             * H_look_around scene sets its "letter found" flag before its
             * one-frame cutscene finishes, which leaves allow_input stuck
             * false; Space bypassing that check is the only way to
             * progress past it, so this quirk is kept rather than
             * "fixed" into a softlock. */
            if (is_space || (is_enter && g_allow_input)) {
                soundfx_play("press");
                if (strcmp(g_state, "running") != 0) text_valg();
                need_redraw = true;
            } else if (ch == KEY_DOWN && g_allow_input) {
                soundfx_play("down");
                if (g_tree_move_selected) {
                    tree_move("down");
                } else {
                    g_valg += 1;
                    if (g_valg == 5) g_valg = 1;
                }
                need_redraw = true;
            } else if (ch == KEY_UP && g_allow_input) {
                soundfx_play("up");
                if (g_tree_move_selected) {
                    tree_move("up");
                } else {
                    g_valg -= 1;
                    if (g_valg == 0) g_valg = 4;
                }
                need_redraw = true;
            } else if (ch == KEY_LEFT && g_allow_input) {
                soundfx_play("down");
                if (g_tree_move_selected) {
                    tree_move("left");
                } else if (strcmp(g_state, "choice") == 0 && g_valg == 2) {
                    g_tree_chapter_load -= 1;
                    if (g_tree_chapter_load <= -1) g_tree_chapter_load = 0;
                    g_tree_on_chapter = false;
                    g_tree_x = 0; g_tree_y = 0;
                    tree_load();
                } else if (strcmp(g_state, "music") == 0 && g_valg == 1) {
                    music_next(-1);
                } else if (strcmp(g_state, "music") == 0 && g_valg == 2) {
                    music_set_volume(g_music.volume - 5);
                } else if (strcmp(g_state, "music") == 0 && g_valg == 3) {
                    soundfx_set_volume(g_soundfx_volume - 5);
                } else if (strcmp(g_state, "screen") == 0 && g_valg == 1) {
                    g_scale -= 0.5f;
                    if (g_scale <= 1) g_scale = 1;
                }
                need_redraw = true;
            } else if (ch == KEY_RIGHT && g_allow_input) {
                soundfx_play("up");
                if (g_tree_move_selected) {
                    tree_move("right");
                } else if (strcmp(g_state, "choice") == 0 && g_valg == 2) {
                    g_tree_chapter_load += 1;
                    int max_chapter = sl_get_max_chapter();
                    if (g_tree_chapter_load >= max_chapter) g_tree_chapter_load = max_chapter;
                    g_tree_on_chapter = false;
                    g_tree_x = 0; g_tree_y = 0;
                    tree_load();
                } else if (strcmp(g_state, "music") == 0 && g_valg == 1) {
                    music_next(1);
                } else if (strcmp(g_state, "music") == 0 && g_valg == 2) {
                    music_set_volume(g_music.volume + 5);
                } else if (strcmp(g_state, "music") == 0 && g_valg == 3) {
                    soundfx_set_volume(g_soundfx_volume + 5);
                } else if (strcmp(g_state, "screen") == 0 && g_valg == 1) {
                    g_scale += 0.5f;
                    if (g_scale >= 6) g_scale = 6;
                }
                need_redraw = true;
            } else if (ch == 'm' || ch == 'M') {
                strncpy(g_state, "menu", sizeof g_state - 1);
                g_tree_is_load = false;
                cut_menu();
                redraw();
            } else if (ch == 'q' || ch == 'Q') {
                running = false;
            } else if (ch == 's' || ch == 'S') {
                if (!g_allow_input) g_skip_cutsceen = true;
                need_redraw = true;
            }
        }

        /* ---- state dispatch (mirrors The_night.py's game loop body) ---- */
        if (strcmp(g_state, "skip") == 0) {
            sf_cutsceen(skip_sequence, FRAME_COUNT(skip_sequence), NULL, g_skip_target_state, g_skip_target_cut);

        } else if (g_chapter == 0) {
            if (strcmp(g_state, "running") == 0) {
                sf_cutsceen(startup_sequence, FRAME_COUNT(startup_sequence), glitch, "menu", cut_menu);

            } else if (strcmp(g_state, "menu") == 0) {
                cut_menu();
                choice_select("opening_cutsceen", NULL,
                               "settings", cut_settings,
                               "choice", cut_choice,
                               "quit", NULL);

            } else if (strcmp(g_state, "settings") == 0) {
                cut_settings();
                choice_select("screen", cut_screen,
                               "music", cut_music,
                               "credits", cut_credits,
                               "menu", cut_menu);

            } else if (strcmp(g_state, "screen") == 0) {
                cut_screen();
                if (g_selected_valg[2]) {
                    if (strcmp(g_shader_on, "ON") == 0) strcpy(g_shader_on, "OFF");
                    else if (strcmp(g_shader_on, "OFF") == 0) strcpy(g_shader_on, "ON");
                }
                choice_select(NULL, NULL,
                               NULL, cut_screen,
                               NULL, NULL,
                               "settings", cut_settings);

            } else if (strcmp(g_state, "credits") == 0) {
                choice_select(NULL, NULL, NULL, NULL, NULL, NULL, "settings", cut_settings);

            } else if (strcmp(g_state, "music") == 0) {
                cut_music();
                choice_select(NULL, NULL, NULL, NULL, NULL, NULL, "settings", cut_settings);

            } else if (strcmp(g_state, "choice") == 0) {
                cut_choice();
                if (!g_tree_is_load) tree_load();
                if (g_selected_valg[1]) g_tree_move_selected = !g_tree_move_selected;
                choice_select(NULL, cut_choice, NULL, NULL, NULL, NULL, "menu", cut_menu);

            } else if (strcmp(g_state, "opening_cutsceen") == 0) {
                sf_cutsceen(opening_cutsceen_list, FRAME_COUNT(opening_cutsceen_list), opening_cutsceen, "H_continue", cut_H_continue);
            }

        } else if (g_chapter == 1) {
            if (strcmp(g_state, "H_continue") == 0) {
                strncpy(g_state, "H_livingroom", sizeof g_state - 1);

            } else if (strcmp(g_state, "H_kitchen") == 0) {
                if (get_plot("item", "knife") || get_plot("item", "bun")) {
                    choice_select(NULL, NULL, NULL, NULL, "H_livingroom", cut_H_livingroom, NULL, NULL);
                } else {
                    choice_select("H_look_for_food", NULL, "H_search_your_kitchen", NULL,
                                   "H_livingroom", cut_H_livingroom, NULL, NULL);
                }

            } else if (strcmp(g_state, "H_look_for_food") == 0) {
                if (!get_plot("item", "bun")) plot_write("item", "bun", true);
                sf_cutsceen(H_look_for_food_cutsceen, FRAME_COUNT(H_look_for_food_cutsceen), H_look_for_food_img, "H_kitchen", cut_H_kitchen);

            } else if (strcmp(g_state, "H_search_your_kitchen") == 0) {
                if (!get_plot("item", "knife")) plot_write("item", "knife", true);
                sf_cutsceen(H_search_your_kitchen_cutsceen, FRAME_COUNT(H_search_your_kitchen_cutsceen), H_search_your_kitchen_img, "H_kitchen", cut_H_kitchen);

            } else if (strcmp(g_state, "H_livingroom") == 0) {
                choice_select("H_sit_down", cut_H_sit_down, "H_kitchen", cut_H_kitchen,
                               "H_room", cut_H_room, NULL, NULL);

            } else if (strcmp(g_state, "H_sit_down") == 0) {
                choice_select("H_livingroom", cut_H_livingroom, "H_tv", NULL, NULL, NULL, NULL, NULL);

            } else if (strcmp(g_state, "H_tv") == 0) {
                sf_cutsceen(H_watch_tv_cutseen, FRAME_COUNT(H_watch_tv_cutseen), H_watch_tv_img, "menu", cut_menu);
                if (!get_plot("plot", "alseep tv")) plot_write("plot", "alseep tv", true);

            } else if (strcmp(g_state, "H_room") == 0) {
                choice_select("H_look_around", cut_H_look_around, "H_lay_down", cut_H_lay_down,
                               NULL, NULL, "H_livingroom", cut_H_livingroom);

            } else if (strcmp(g_state, "H_look_around") == 0) {
                if (!get_plot("item", "letter")) {
                    sf_cutsceen(H_look_around_cutsceen, FRAME_COUNT(H_look_around_cutsceen), H_look_around_img, "H_room", cut_H_room);
                    plot_write("item", "letter", true);
                }
                choice_select("H_room", cut_H_room, NULL, NULL, NULL, NULL, NULL, NULL);

            } else if (strcmp(g_state, "H_lay_down") == 0) {
                choice_select("H_room", cut_H_room, "H_fall_asleep", NULL, NULL, NULL, NULL, NULL);

            } else if (strcmp(g_state, "H_fall_asleep") == 0) {
                sf_cutsceen(H_fall_asleep_cutsceen, FRAME_COUNT(H_fall_asleep_cutsceen), H_fall_asleep_img, "menu", cut_menu);
                if (!get_plot("plot", "alseep tv")) plot_write("plot", "alseep tv", true);
            }
        }

        if (need_redraw) {
            /* original also has `if sf.state == "quit": running = False`
               here; tree.draw() for state=="choice" is folded into
               redraw() itself in this port, so it isn't called separately. */
            if (strcmp(g_state, "quit") == 0) running = false;
            redraw();
            need_redraw = false;
        }
    }

    endwin();
    return 0;
}
