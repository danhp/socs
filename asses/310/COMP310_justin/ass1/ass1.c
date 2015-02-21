/*
 * COMP 310 - Assignment 1
 * Justin Domingue - 260588454
 *
 *          README
 * ---------------------------
 * 
 * the foreground command will only be added to the history if they were successful
 *        (execvp returned 0)
 * the background command are always added to the history as there is no straightforward
 *        way to tell if the command was successful - the shell assumes they were
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>
#include <string.h>

#define MAX_LINE 80   /* 80 chars per line, per command, should be enough. */
#define MAX_JOBS 20   /* # of background jobs allowed at the same time */

#define TRUE  1 
#define FALSE 0

/* ----------- GLOBAL VARIABLES AND STRUCTURES ----------- */

/* history[][] holds the shell command history. The first element of the array
 * is always the most recent command (other elements shifts when new command is
 * executed)
 */
char history[10][MAX_LINE] = {{0}};   /* holds command history - initialize to 0 */
int history_count = 0;                /* # of commands entered by the user */
char history_buffer[MAX_LINE];

/* Define chpid globally so that the signal handler has access to it */
pid_t chpid;

/* a single process - does not implement pipelines of processes */
typedef struct job
{
  struct job *next;   /* next process in pipeline */
  pid_t pid;          /* process ID */
  char command[MAX_LINE];       /* command */
} job;

/* the active jobs are linked into a list. This is its head. */
job *first_job = NULL;

/* ----------- PROTOTYPES ----------- */

void addJob(char *command);
char *findCommand(char c);

/* ----------- SIGNALS HANDLING ----------- */

/* The signal handler function for <C-z> */
static void handle_SIGTSTP(int sig)
{
  /* add the job to the jobs linked list */
  /* remember that history[0] is a string version of args which was passed to execvp */
  addJob(history[0]);

  /* put chpid into the background */
  kill(chpid, SIGSTOP);
}

static void handle_SIGINT(int sig)
{
  /* do nothing */
  return;
}

/* ----------- JOBS HANDLING ----------- */

/* Find the active job with the indicated pid */
int findJob(pid_t pid)
{
  job *j;

  for (j = first_job; j; j = j->next)
    if (j->pid == pid)
      return TRUE;
  return FALSE;
}

/* createJobsList() creates the linked list containing the jobs */
void createJobsList(pid_t pid, char *command)
{
  job *j = (job*)malloc(sizeof(job));

  /* Check if malloc was successful */
  /* Commented because of parent/child problem (j is NULL in child) */
  /* if (NULL == j) { */
  /*   printf("Job creation failed.\n"); */
  /*   exit(-1); */
  /* } */

  j->pid = pid;
  strcpy(j->command, command);
  j->next = NULL;

  first_job= j;
}

/* add a job to the job linked list */
/* most of the time, history[0] will be passed to the function
 *    as it is formatted in a string, usable by the job struct
 */
void addJob(char *command)
{
  /* check if a node with same pid exists */
  if (findJob(chpid))
    return;

  /* check if list is empty* */
  if (NULL == first_job) {
    createJobsList(chpid, command);
    return;
  }

  job *j = first_job;
  job *new_job = (job*)malloc(sizeof(job));

  new_job->pid = chpid;
  strcpy(new_job->command, command);
  new_job->next = NULL;

  /* Find where to insert */
  while (j->next != NULL)
    j = j->next;

  j->next = new_job;
}

/* deleteJob will delete job with PID pid */
int deleteJob(pid_t pid)
{
  job *prev = NULL;
  job *del = NULL;
  job *curr = first_job;

  //printf("\n Deleting value [%d] from list\n",pid);

  /* find the job we want to delete, keeping track of the previous one */
  while(curr != NULL) {

    if (curr->pid == pid) {
      /* we have found the node we want to delete */
      del = curr;
      break;
    } else {
      prev = curr;
      curr = curr->next;
    }
  }

  if(del == NULL)
    return -1;
  else {
    if(prev != NULL)
      /* remove del from the linked list */
      prev->next = del->next;
    else if(del == first_job)
      /* first_job is now the second job */
      first_job = del->next;
  }

  /* free the deleted node */
  free(del);
  del = NULL;

  return 0;
}

void printJobs()
{
  /* first check if job is non-empty */
  if (first_job == NULL) {
    printf("No jobs currently running.\n");
    return;
  }

  job *j = first_job;

  /* print each node of the linked list */
  while (j != NULL) {
    printf("[%d] %s\n", j->pid, j->command);
    j = j->next;
  }
}

/* ----------- HISTORY ----------- */

void addToHistory(char *args[MAX_LINE]) 
{
  int i, j, k = 0;
  char command[MAX_LINE];

  /* Before shifting the elements, save the oldest to the buffer
   * in case the command added was erroneous (allows to restore the
   * history array) */
  strcpy(history_buffer, history[9]);

  /* Shift the first 9 elements of the history 2D array (drop the last one) */
  for(i=8;i>=0;i--)
    strcpy(history[i+1], history[i]);

  /* Stringify args */
  for (i = 0; args[i] != NULL; i++) {         /* Parse each argument */
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

void removeMostRecentFromHistory()
{
  int i;

  /* decrement history_count */
  history_count--;

  /* shift all elements to the left */
  for(i = 0; i < 9; i++)
    strcpy(history[i], history[i+1]);

  /* restore the oldest command */
  strcpy(history[9], history_buffer);

  return;
}

/* Returns -1 if history is empty and 0 otherwise */
int historyIsEmpty() {
  if (strcmp(history[0], "\0") == 0) {
    printf("History is empty.\n");
    return TRUE;
  }

  /* Return true */
  return FALSE;
}

/* findCommand() finds a command in history by __first character__ only */
char *findCommand(char c)
{
  int i = 0;

  /* check if history is empty */
  if (historyIsEmpty()) return NULL;

  /* Iterate trough history starting with the most recent,
   * and return the entry if first character matches */
  for (i = 0; i < 9; i++)
    if (history[i][0] == c)
      return history[i];

  /* Command not found, empty string */
  return NULL;
}

void printHistory()
{
  int i;

  /* First check if history is empty */
  if (historyIsEmpty()) return;

  /* Loop through the history array and print */
  for (i = 0; i < 10 && (strcmp(history[i], "\0") != 0); i++)
    printf("%d %s\n", history_count - i, history[i]);       /* print entry number */

  return;
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

  char tmp_cmd[MAX_LINE];

  ct = 0;

  /* read what the user enters on the command line */
  length = read(STDIN_FILENO, inputBuffer, MAX_LINE);

  start = -1;
  if (length == 0)
    exit(0);        /* ^d entered, end of user command stream */

  /* length of 01 could mean two things :
   *    i) error in reading
   *    ii) read() was interrupter (no error)
   * so we need to check for the environment variable called errno
   */
  if ((length < 0) && (errno != EINTR)) {
    perror("error reading the command\n");
    exit(-1);       /* terminate with error code -1 */
  }

  /* HISTORY ---------------------------------------------------------- */
  /* Before parsing the inputBuffer, check if user wants to use history */
  if (inputBuffer[0] == 'r') {

    /* If history is empty, return error */
    if (historyIsEmpty()) return FALSE;

    if (inputBuffer[1] == '\n') {         /* most recent command */

      printf("Most recent command: %s\n", history[0]);

      /* Copy the command into the args array, readable by execvp */
      for (i = 0; history[0][i] != '\0'; i++) {           /* Loop through each character */
        if (history[0][i] != ' ') {           /* If not a space */
          args[k][j++] = history[0][i];       /*    add to array cell */
        } else {
          args[k][j] = '\0';                  /* add null character */
          k++;                                /* next parameter */
          j = 0;                              /* new array cell, reset j */
        }
      }

      /* For execvp */
      args[++k] = NULL;

    } else if (inputBuffer[1] == ' ') {   /* command by number */

      /* copy history command into args */
      strcpy(tmp_cmd, findCommand(inputBuffer[2]));  /* inputBuffer[2] is command number */

      /* Command was not found */
      if (tmp_cmd[0] == '\0') {
        printf("Command not found in history.\n");
        return -1;
      }

      printf("History command: %s\n", tmp_cmd);

      /* Copy the command into the args array, readable by execvp */
      for (i = 0; tmp_cmd[i] != '\0'; i++) {           /* Loop through each character */
        if (tmp_cmd[i] != ' ') {           /* If not a space */
          args[k][j++] = tmp_cmd[i];       /*    add to array cell */
        } else {
          args[k][j] = '\0';                  /* add null character */
          k++;                                /* next parameter */
          j = 0;                              /* new array cell, reset j */
        }
      }

      /* For execvp */
      args[++k] = NULL;

    }
    return TRUE;
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

          if (start == i)
            start = -1;
        }
    }
  }
  args[ct] = NULL;  /* just in case the input line was > 80 */  

  /* Before returning TRUE, make sure args[] is set */
  if (args[0] != NULL)
    return TRUE;
  else
    return FALSE;
}

int main(void)
{
  char inputBuffer[MAX_LINE]; /* buffer to hold the command entered */
  int background;             /* equals 1 if a command if followed by '&' */
  char *args[MAX_LINE];    /* command line (of 80) has max 40 arguments */
  char built_in[MAX_LINE];  /* will be overwritten if a built-in command is called */

  /* don't forget, pid_t chpid was defined globally */
  int status = 0;                 /* filled on child's exit */

  /* Ignore CTRL-C */
  signal(SIGINT, &handle_SIGINT);

  /* set up the signal handler for <C-z> */
  struct sigaction handler;
  memset(&handler, 0, sizeof handler);
  handler.sa_handler = handle_SIGTSTP;
  sigaction(SIGTSTP, &handler, NULL);

  while (1) {                 /* Proram terminates normally inside setup */
    background = 0;
    printf("COMMAND->\n");

    /* Get next command - verify if the parsing was successful ; if not, re-ask for the command */
    if (!setup(inputBuffer, args, &background)) continue;

    /* BUILT-IN COMMANDS --------------------------------- */
    /* Before issuing the command to the system with execvp,
     * check if it is a built-in command in the shell */
    /* Note : I could have use one big if statement for built-in commands
     *    and the fork process (fork would have been in an "else"), but I
     *    prefer to separate the different logic blocks with different if
     *    statements and continue/break statements
     */
  
    strcpy(built_in, "null");

    if (strcmp(args[0], "history") == 0) {
      printHistory();
      strcpy(built_in, "history");
    } else if (strcmp(args[0], "cd") == 0) {
      /* call chdir and save return status */
      status = chdir(args[1]);

      /* if status is no 0, the chdir did not go through (error) */
      if (status != 0)
        perror("Error");

      /* copy the command into built_in which will go into history */
      strcpy(built_in, "cd");
    } else if (strcmp(args[0], "exit") == 0) {
      /* Print an exit text and break the while loop */
      printf("Exiting the shell\n");
      break;
    } else if (strcmp(args[0], "jobs") == 0) {
      printJobs();

      /* copy the command into built_in which will go into history */
      strcpy(built_in, "jobs");
    } else if (strcmp(args[0], "fg") == 0) {

      if (args[1] == NULL) {
        printf("No job ID provided.\n");
        continue;
      }

      /* conveniently, setup will have put the chpid inside args[1] */
      pid_t job_pid = atoi(args[1]);

      /* look for a job with the specified id */
      if (!findJob(job_pid))
        printf("No job with pid [%d] found.\n", job_pid);
      else {
        /* Job was found, put it on the foreground */
        printf("Sending job [%d] to the foreground.\n", job_pid);

        /* remove job from the job list */
        deleteJob(job_pid);

        /* Resume the process */
        kill(job_pid, SIGCONT);
      }
      /* copy the command into built_in which will go into history */
      strcpy(built_in, "fg");
    } 

    /* Check if built-in command was used. If yes, add to history */
    if (strcmp(built_in, "null")) {
      /* command command to args */
      strcpy(args[0], built_in);
      args[1] = NULL;

      /* add command to history */
      addToHistory(args);

      /* Empty built_in */
      built_in[0] = '\0';
      continue;
    }

    /* FORK PROCESS ----------------- */
    /* Create a child by calling fork */
    chpid = fork();             

    if (chpid == 0) {           /* Inside the child */
      /* Execute the command with the options */
      status = execvp(args[0], args);  

      /* Exit with status */
      exit(status);
    } else {                  /* Inside the parent */
      if (background == 1) {      
        /* Add command to history - assume it was successful */
        addToHistory(args);

        printf("Launching job [%d] in background.\n", chpid);

        /* Add job to job structure */
        addJob(history[0]);

        /* put the command in the background */
        kill(chpid, SIGSTOP);
      } else {                    

        /* add command to history */
        addToHistory(args);

        /* wait for child to finish */
        /* save the exit status of the child inside status */
        waitpid(chpid, &status, WUNTRACED);

        if (WIFSTOPPED(status))
          kill(chpid, SIGCONT);

        /* was command successful? */
        if (status != 0)  {
          printf("Command was detected erroneous.\n");

          /* the command was added to the history earlier so that the
           * signals could access it. Remove it. */
          removeMostRecentFromHistory();
        }
      }
    }
  }

  return 0;
}
