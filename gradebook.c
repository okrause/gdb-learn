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

/* Recursively walk the list and return the student with the highest average. */
static Student *best_of(Student *a, Student *b)
{
    if (a == NULL) {
        return b;
    }
    if (b == NULL) {
        return a;
    }
    return (a->average >= b->average) ? a : b;
}

static Student *find_top(Student *head)
{
    if (head == NULL || head->next == NULL) {
        return head;
    }
    return best_of(head, find_top(head->next));
}

static float compute_average(const Score *scores, int n)
{
    float sum = 0.0f;
    int i;

    for (i = 0; i < n; i++) {
        sum += scores[i].points;
    }

    /* BUG: should be `return sum / n;`  Off-by-one in the divisor. */
    return sum / (n + 1);
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
    s->next = NULL;

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

static void print_roster(const Student *head)
{
    const Student *cur;

    puts(" id   name            avg   scores");
    puts("----  --------------  ----  --------------------");
    for (cur = head; cur != NULL; cur = cur->next) {
        int i;

        printf("%4d  %-14s  %4.1f  ", cur->id, cur->name, cur->average);
        for (i = 0; i < cur->n_scores; i++) {
            printf("%s=%.0f%s",
                   cur->scores[i].label,
                   cur->scores[i].points,
                   (i + 1 < cur->n_scores) ? "," : "");
        }
        putchar('\n');
    }
}

static void free_roster(Student *head)
{
    while (head) {
        Student *n = head->next;
        free(head);
        head = n;
    }
}

int main(void)
{
    Student *roster = NULL;
    Student *top;
    const float ada[] = {90, 88, 94, 91};
    const float alan[] = {70, 75, 68, 80};
    const float grace[] = {100, 98, 97, 99};

    push_front(&roster, make_student("Ada", 101, ada, 4));
    push_front(&roster, make_student("Alan", 102, alan, 4));
    push_front(&roster, make_student("Grace", 103, grace, 4));

    print_roster(roster);

    top = find_top(roster);
    printf("\nTop student: %s (avg %.1f)\n", top->name, top->average);

    free_roster(roster);
    return 0;
}
