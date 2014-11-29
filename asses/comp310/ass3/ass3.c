// User level threading library.
// Written by Daniel Pham
// 260 526 252

#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ucontext.h>

#define TRUE 1
#define FALSE 0

#define RUNNABLE 2
#define BLOCKED 3
#define EXIT 4

#define THREAD_NAME_LEN 80
#define TABLE_SIZE 10

typedef struct mythread_control_block{
    ucontext_t context;
    char thread_name[THREAD_NAME_LEN];
    int thread_id;
    int state;
    int time_run;
} mythread_control_block;

typedef struct semaphore{
    int id;
    int count;
    struct semaphore *next;
    struct list_element *firstElement;
} semaphore;

typedef struct list_element{
    int thread_id;
    struct list_element *next;
} list_element;

typedef struct run_element{
    ucontext_t context;
    int thread_id;
    struct run_element *next;
} run_element;

// Global structures
semaphore *firstSemaphore;
run_element *run_queue;
mythread_control_block* table[TABLE_SIZE];
int thread_count;
int running_id;
int quantum_time;


/* LIBRARY FUNCTIONS */

int mythread_init(){
    firstSemaphore = NULL;
    run_queue = NULL;
    thread_count = 0;
    quantum_time = 0;
    running_id = -1;
    for (int i = 0; i < TABLE_SIZE; i++){
        table[i] = NULL;
    }

    return 0;
}

int mythread_create(char *threadName, void (*threadfunc)(), int stacksize){
    if (thread_count >= TABLE_SIZE){
        perror("Control block is full");
        return -1;
    }

    ucontext_t new_context;
    getcontext(&new_context);

    //Modify its stack
    new_context.uc_link = 0;
    new_context.uc_stack.ss_sp = malloc(stacksize);
    new_context.uc_stack.ss_size = stacksize;
    new_context.uc_stack.ss_flags = 0;
    if (new_context.uc_stack.ss_sp == 0){
        perror("malloc: Could not allocate the stack");
        return -1;
    }

    // Create the new context
    makecontext(&new_context, threadfunc, 0);

    // Initialize an entry in the table
    mythread_control_block *new_mcb = (mythread_control_block*)malloc(sizeof(mythread_control_block));
    new_mcb->context = new_context;
    strcpy(new_mcb->thread_name, threadName);
    new_mcb->thread_id = thread_count;
    new_mcb->state = RUNNABLE;
    new_mcb->time_run = 0;

    // Add to table
    table[thread_count] = new_mcb;
    thread_count++;

    // Init a run_queue element
    run_element *new_e = (run_element*)malloc(sizeof(run_element));
    new_e->context = new_mcb->context;
    new_e->thread_id = new_mcb->thread_id;
    new_e->next = NULL;

    // Append to run_queue
    run_element *r = run_queue;
    if (r == NULL){
        r = new_e;
    } else {
        while (r->next != NULL){
            r = r->next;
        }
        r->next = new_e;
    }

    return 0;
}

void mythread_exit(){
    // Remove from run queue.
    run_element *to_remove = run_queue;
    if (run_queue != NULL){
        run_queue = run_queue->next;
    }
    free(to_remove);

    //Find the matching entry and update state.
    if (running_id > -1 && table[running_id] != NULL){
        table[running_id]->state = EXIT;
    }
}

void runthreads(){

}

void set_quantum_size(int quantum){
    quantum_time = quantum;
}

int create_semaphore(int semValue){
    semaphore *s = firstSemaphore;
    semaphore *newSemaphore = (semaphore*)malloc(sizeof(semaphore));

    //Init the new semaphore
    newSemaphore->count = semValue;
    newSemaphore->firstElement = NULL;

    if (firstSemaphore == NULL){
        newSemaphore->id = 1;
        firstSemaphore = newSemaphore;
    } else {
        while (s->next != NULL){
            s = s->next;
        }
        newSemaphore->id = s->id + 1;
        s->next = newSemaphore;
    }

    return newSemaphore->id;
}

void semaphore_wait(int semId){
    // Get semaphore
    semaphore *s = firstSemaphore;
    while (s->id != semId && s != NULL){
        s = s->next;
    }

    // Impletments the semaphore
    if (s != NULL){
        s->count = s->count - 1;
        if (s->count < 0){
            list_element *newElement = (list_element*)malloc(sizeof(list_element));
            s->firstElement = newElement;
        }
    }
}

void semaphore_signal(int semId){
    // Get semaphore
    semaphore *s = firstSemaphore;
    while (s->id != semId && s != NULL){
        s = s->next;
    }

    //Implements the semaphore
    if (s != NULL){
        s->count = s->count + 1;
        if (s->count >=0){
            int threadToRun = s->firstElement->thread_id;
            s->firstElement = s->firstElement->next;
        }
    }
}

void destroy_semaphore(int semId){
    semaphore *currentSem = firstSemaphore;
    semaphore *previousSem = NULL;

    while (currentSem != NULL){
        if (currentSem->id == semId){
            break;
        } else {
            previousSem = currentSem;
            currentSem = currentSem->next;
        }
    }

    if (previousSem != NULL){
        previousSem->next = currentSem->next;
    } else {
        firstSemaphore = currentSem->next;
    }

    free(currentSem);
}

void mythread_state(){
    mythread_control_block *current_block;
    for (int i = 0; i < TABLE_SIZE && table[i] != NULL; i++){
        current_block = table[i];
        // Print: thread_name, state, time_run
        printf("State description: \n");
        printf("Thread Name: %s, State: %d, Time run: %d.\n", current_block->thread_name, current_block->state, current_block->time_run);
    }
}

int main(){
    mythread_init();
    create_semaphore(3);
    mythread_exit();
    mythread_state();
    // printf("This: %d\n", firstSemaphore->id);

    return 0;
}
