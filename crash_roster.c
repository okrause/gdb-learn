#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SCORES 4
#define NAME_LEN   32

typedef struct {
    char  label[8];
    float points;
} Score;

typedef struct Student {
    char            name[NAME_LEN];
    int             id;
    Score           scores[MAX_SCORES];
    int             n_scores;
    float           average;
    struct Student *next;
} Student;

static float compute_average(const Score *scores, int n)
{
    float sum = 0.0f;
    int i;

    for (i = 0; i < n; i++) {
        sum += scores[i].points;
    }
    return (n > 0) ? (sum / n) : 0.0f;
}

static Student *make_student(const char *name, int id, const float *points, int n)
{
    static const char *labels[] = {"quiz", "hw", "mid", "fin"};
    Student *s = malloc(sizeof(*s));
    int i;

    if (s == NULL) {
        perror("malloc");
        exit(1);
    }
    memset(s, 0, sizeof(*s));
    strncpy(s->name, name, NAME_LEN - 1);
    s->id = id;
    s->n_scores = n;
    for (i = 0; i < n && i < MAX_SCORES; i++) {
        strncpy(s->scores[i].label, labels[i], sizeof(s->scores[i].label) - 1);
        s->scores[i].points = points[i];
    }
    s->average = compute_average(s->scores, s->n_scores);
    return s;
}

static void push_front(Student **head, Student *s)
{
    s->next = *head;
    *head = s;
}

static Student *find_by_id(Student *head, int id)
{
    Student *cur = head;

    while (cur != NULL) {
        if (cur->id == id) {
            return cur;
        }
        cur = cur->next;
    }
    return NULL; /* caller must check — this tutorial does not */
}

static void announce_top(Student *s)
{
    /* Crashes here when s is NULL (missing id) or when s is freed (UAF). */
    printf("Selected: %s (id %d, avg %.1f)\n", s->name, s->id, s->average);
}

static void free_roster(Student *head)
{
    while (head) {
        Student *n = head->next;
        free(head);
        head = n;
    }
}

static Student *build_roster(void)
{
    Student *roster = NULL;
    const float ada[] = {90, 88, 94, 91};
    const float alan[] = {70, 75, 68, 80};
    const float grace[] = {100, 98, 97, 99};

    push_front(&roster, make_student("Ada", 101, ada, 4));
    push_front(&roster, make_student("Alan", 102, alan, 4));
    push_front(&roster, make_student("Grace", 103, grace, 4));
    return roster;
}

int main(int argc, char **argv)
{
    Student *roster = build_roster();
    Student *chosen;
    int want_id = 999; /* default: id that does not exist */
    int use_after_free = 0;

    if (argc >= 2) {
        if (strcmp(argv[1], "uaf") == 0) {
            use_after_free = 1;
        } else {
            want_id = atoi(argv[1]);
        }
    }

    if (use_after_free) {
        chosen = find_by_id(roster, 103);
        free_roster(roster);
        roster = NULL;
        /* chosen still points at freed Grace */
        announce_top(chosen);
        return 0;
    }

    chosen = find_by_id(roster, want_id);
    announce_top(chosen);
    free_roster(roster);
    return 0;
}
