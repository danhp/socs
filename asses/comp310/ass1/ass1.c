//Written by Daniel Pham
// 260 526 252

#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#define MAX_LINE 80 /* 80 chars per line, per command, should be enough. */
#define MAX_HISTORY 10
/**
* setup() reads in the next command line, separating it into distinct tokens
* using whitespace as delimiters. setup() sets the args parameter as a 
* null-terminated string.
*/
char *history[MAX_HISTORY];
int historyCount = 0;
int jobCount = 0;
pid_t chpid;

//Represents a backround process
typedef struct job {
    struct job *next;
    pid_t pid;
    char command[MAX_LINE];
} job;

job *firstJob = NULL;

void addJob(char *command) {
    job *j = firstJob;
    job *newJob = (job*)malloc(sizeof(job));

    newJob->pid = chpid;
    strcpy(newJob->command, command);
    newJob->next = NULL;

    if (j == NULL){
        firstJob = newJob;
    } else {
        while (j->next != NULL)
            j = j->next;
        
        j->next = newJob;
    }
}

void removeJob(pid_t pid){
    job *current = firstJob;
    job *previous = NULL;
    firstJob = NULL;
    
    while (current != NULL){
        if (current->pid == pid){
            break;
        } else {
            previous = current;
            current = current->next;
        }
    }
    
    if (previous != NULL){
        previous->next = current->next;
    } else {
        firstJob = current->next;
    }
    
    free(current);
}

int setup(char inputBuffer[], char *args[],int *background){
    int length,     /* # of characters in the command line */
    i,              /* loop index for accessing inputBuffer array */
    start,          /* index where beginning of next command parameter is */
    ct;             /* index of where to place the next parameter into args[] */

    ct = 0;
    
    //should be succes unless encounter error cases.
    int result = 1;
    
	/* read what the user enters on the command line */
    length = read(STDIN_FILENO, inputBuffer, MAX_LINE); 

    start = -1;
    if (length == 0){
		exit(0);  //^d was entered, end of user command stream
	}
    if (length < 0){
        perror("error reading the command");
        exit(-1); /* terminate with error code of -1 */
    }
        
    //Implement r
    if (strncmp("r", inputBuffer, 1) == 0){
        strsep(&inputBuffer, " ");
        char *letter = strsep(&inputBuffer, "\n");
        int k = 0; 
        for (k; k < MAX_HISTORY && (history[k] != NULL); k++){
            if (strncmp(letter, history[k], 1) == 0){
                printf(" >Running: %s\n", history[k]);
                inputBuffer = strdup(history[k]);
                strcat(inputBuffer, "\n");
                break;
            }
        }
        //No matching history found.
        if (k > MAX_HISTORY || history[k] == NULL){
            printf("No Match\n");
            
            fflush(stdout);
            return 0;
        }
    }
    
    //Implements history
    if (strncmp("history", inputBuffer, 7) == 0){
        result = 0;
        if (historyCount == 0)
            return result;
        int j, k;
        for (j = historyCount%10, k = 0; k < MAX_HISTORY; k++){
            if (history[j] != NULL){
                if (j < historyCount%10){
                    printf("%d. %s\n", ((historyCount-1)/10)*10 + j + 1, history[j]);
                    fflush(stdout);
                } else {
                    printf("%d. %s\n", (historyCount-j-1)/10*10 + j + 1, history[j]);
                    fflush(stdout);
                }
            }
            if (j < MAX_HISTORY - 1){
                j++;
            } else {
                j = 0;
            }
        }
    }else{
        if (strncmp("r", inputBuffer, 1) != 0){
            history[historyCount%10] = strdup(inputBuffer);
            history[historyCount%10] = strsep(&history[historyCount%10], "\n");
            historyCount++;
        }
    }

    //Implements exit
    if (strncmp("exit", inputBuffer, 4) == 0){
        exit(0);
    }

    /* examine every character in the inputBuffer */
    length = strlen(inputBuffer);
    for (i=0; i < length; i++) { 
        switch (inputBuffer[i]){
            case ' ':
                //Do nothing
            case '\t' : /* argument separators */
                if(start != -1){
                    args[ct] = &inputBuffer[start]; /* set up pointer */
                    ct++;
                }
                inputBuffer[i] = '\0';    /* add a null char; make a C string */
                start = -1;
                break;
            case '\n':                   /* should be the final char examined */
                if (start != -1){
                    args[ct] = &inputBuffer[start]; 
                    ct++;
                }
                inputBuffer[i] = '\0';
                args[ct] = NULL;         /* no more arguments to this command */
                break;
            default : /* some other character */
                if (start == -1)
                    start = i;
                if (inputBuffer[i] == '&'){
                    *background = 1;
                    inputBuffer[i] = '\0';
                    start = -1;
                }
        }
    } 
    args[ct] = NULL;                   /* in case the input line was > 80 */
    return result;

}
int main(void){
    char inputBuffer[MAX_LINE];         /* buffer to hold the command entered */
    int background;                     /* 1 if command is followed by '&' */
    char *args[MAX_LINE/+1];            /* line has max of 40 arguments */
    int status;
    int builtIn;
    int success;
 
    while (1){                          /* Program terminates normally inside setup */
        background = 0;
        status = 0;
        printf("COMMAND-> ");
        fflush(stdout);
        
        success = setup(inputBuffer,args,&background);
        if (!success){
            continue;
        }
        
        //Implements change directory
        if (strncmp("cd\0", inputBuffer, 3) == 0){;
            chdir(args[1]);
            continue;
        }

        //Implements current working directory
        if (strncmp("pwd\0", inputBuffer, 5) == 0){
            char cwd[1024];
            getcwd(cwd, sizeof(cwd));
            printf("%s\n", cwd);
            continue;
        }
            
        //Print jobs
        if (strncmp("jobs\0", inputBuffer, 6) == 0){
            if (firstJob == NULL) {
                printf("No jobs running.\n");
            }

            job *j = firstJob;
            while (j != NULL) {
                printf("[%d] %s\n", j->pid, j->command);
                j = j->next;
            }
            continue;
        }
        
        if (strncmp("fg\0", inputBuffer, 3) == 0){
            if (args[1] == NULL) {
                continue;
            }
            
            pid_t jobPid = atoi(args[1]);
            waitpid(jobPid, &status, 0);
            removeJob(jobPid);
            continue;
        }
        
        if (chpid = fork()){
            //parent process
            sleep(1);
            if (background == 0){
                waitpid(chpid, &status, 0);
            }else{
                addJob(args[0]);
            }
        }else{
            //child process
            execvp(*args, args);
            removeJob(chpid);
            exit(0);
        }
    }
}
