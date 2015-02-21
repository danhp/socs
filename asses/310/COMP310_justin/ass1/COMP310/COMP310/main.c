#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

#define MAX_LINE 80   /* 80 chars per line, per command, should be enough. */

/* history[][] holds the shell command history. The first element of the array
 * is always the most recent command (other elements shifts when new command is
 * executed)
 */
char history[10][MAX_LINE];   /* holds command history */
int history_count = 0;        /* # of commands entered by the user */

/* The signal handler function */
void handle_SIGINT()
{
    write(STDIN_FILENO, "Signal interrupt\n", 100);
    exit(0);
}

/* findCommand() finds a command in history by __first character__ only */
char *findCommand(char c)
{
    int i = 0;
    
    /* Iterate trough history starting with the most recent,
     * and return the entry if first character matches */
    for (i = 0; i < 9; i++)
        if (history[i][0] == c)
            return history[i];
    
    /* Command not found, empty string */
    return NULL;
}

/*
 * setup() reads in the next command line, separating it into distinct tokens
 * using whitespace as delimiters. setup() sets the args parameter as a
 * null-terminated sting.
 */
int setup(char inputBuffer[], char *args[], int *background)
{
    int length,   /* # of characters in the command line */
    i,        /* loop index for accessing inputBuffer array */
    start,    /* index where beginning of next command parameter is */
    ct;       /* index of where to place the next parameter into args[] */
    
    int j = 0,
    k = 0;
    
    ct = 0;
    
    /* read what the user enters on the command line */
    length = read(STDIN_FILENO, inputBuffer, MAX_LINE);
    
    start = -1;
    if (length == 0)
        exit(0);        /* ^d entered, end of user command stream */
    if (length < 0) {
        perror("error reading the command");
        exit(-1);       /* terminate with error code -1 */
    }
    
    /* Before parsing the inputBuffer, check if user wants to use history */
    if (inputBuffer[0] == 'r') {
        if (inputBuffer[1] == '\n') {         /* most recent command */
            
            printf("Most recent command:  %s\n", history[0]);
            
            /* Copy the command into the args array, readable by execvp */
            for (i = 0; i < MAX_LINE; i++) {
                if (history[0][i] != ' ') {
                    /* args[k][j++] = history[0][i]; */
                } else {
                    args[k][j] = '\0';  /* add null character */
                    k++;                /* next parameter */
                    j = 0;              /* new array cell, reset j */
                }
            }
            
            return 0;
        } else if (inputBuffer[1] == ' ') {   /* command by number */
            
            /* copy history command into args */
            strcpy(args[0], findCommand(inputBuffer[2]));  /* inputBuffer[2] is command number */
            
            /* Command was not found */
            /* if (strncmp(args[0], NULL, MAX_LINE) == 0) */
            /*   return -1; */
            
            printf("History command: %s\n", history[0]);
            return 0;
        }
    }
    
    /* examine every character in the inputBuffer */
    for (i=0;i<length;i++) {
        switch (inputBuffer[i]) {
            case ' ':
            case '\t':    /* argument separators */
                if (start != -1) {
                    args[ct] = &inputBuffer[start]; /* set up pointer */
                    ct++;
                }
                inputBuffer[i] = '\0';  /* add a null char; make a C string */
                start = -1;
                break;
            case '\n':    /* final char examined */
                if (start != -1) {
                    args[ct] = &inputBuffer[start];
                    ct++;
                }
                inputBuffer[i] = '\0';
                args[ct] = NULL;  /* no more arguments to this command */
                break;
            default:      /* some other character */
                if (start == -1)
                    start = i;
                if (inputBuffer[i] == '&') {
                    *background = 1;
                    inputBuffer[i] = '\0';
                }
        }
    }
    args[ct] = NULL;  /* just in case the input line was > 80 */
    
    return 0;
}

void addToHistory(char *args[MAX_LINE])
{
    int i, j, k = 0;
    char command[MAX_LINE];
    
    /* Shift the first 9 elements of the history 2D array (drop the last one) */
    for(i=8;i>=0;i--)
        strcpy(history[i+1], history[i]);
    
    /* Stringify args */
    for (i = 0; args[i] != NULL; i++) {                       /* Parse each argument */
        for (j = 0; args[i][j] != '\0'; j++) {    /* Character by character */
            command[k++] = args[i][j];
        }
        command[k++] = ' ';     /* add space between arguments */
    }
    
    /* Terminate string properly */
    command[k] = '\0';
    
    /* Add command to history array */
    strcpy(history[0], command);
    
    /* Increment history count */
    history_count++;
    
}

int main(void)
{
    char inputBuffer[MAX_LINE]; /* buffer to hold the command entered */
    int background;             /* equals 1 if a command if followed by '&' */
    char *args[MAX_LINE/+1];    /* command line (of 80) has max 40 arguments */
    
    pid_t pid;                  /* will be used by fork */
    int status;                 /* filled on child's exit */
    
    /* set up the signal handler */
    struct sigaction handler;
    handler.sa_handler = handle_SIGINT;
    sigaction(SIGINT, &handler, NULL);
    
    while (1) {                 /* Proram terminates normally inside setup */
        background = 0;
        printf("COMMAND->\n");
        
        /* get next command - verify if the parsing was successful ; if not, re-ask for the command */
        if (setup(inputBuffer, args, &background) != 0) {    /* get next command */
            printf("Command not recognized by the parser.\n");
            continue;
        }
        
        pid = fork();             /* Create a child by calling fork */
        
        /* call addToHistory inside parent */
        addToHistory(args);
        
        if (pid == 0) {           /* Inside the child */
            execvp(args[0], args);  /* Execute the command with the options */
            exit(0);                /* Exit without error */
        } else {                  /* Inside the parent */
            if (background == 1) {      
                /* return to the setup() function */
                continue;
            } else {                    
                /* wait for child to finish */
                waitpid(pid, &status, 0);
            }
        }
    }
    
}
