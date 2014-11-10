// Written by Daniel Pham
// 260 526 252

#include <stdio.h>
#include <stdlib.h>

#define TRUE 1
#define FALSE 0
#define THREAD_NAME_LEN 50

//Index each entry in an array.
typedef struct _mythread_control_block{
    ucontext_t context;
    char thread_name[THREAD_NAME_LEN];
    int thread_id;
} mythread_control_block;


int mythread_init(){

    return 0;
}

int mythread_create(char *threadName, void (*threadfunc)(), int stacksize){

    return 0;
}

void mythread_exit(){

}

void runthreads(){

}

void set_quantum_sizd(int quantum){

}

int create_semaphore(){

    return 0;
}

//Implemented with a semaphore table.
void semaphore_wait(int semaphore){

}

void semaphore_signal(int semaphore){

}

void destroy_semaphore(int semaphore){

}

void mythread_state(){

}
