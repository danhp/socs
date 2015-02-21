/*
 * File: sfs_api.c
 * Author: Justin Domingue - 260588454
 * Date: Thu 03 Apr 2014 06:34:44 PM EDT
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <string.h>

#include "disk_emu.h"

/* ---------- DEFINITION ---------- */

#define MAX_FILES 300       // maximum number of files
#define BLOCK_SIZE 1000
#define MAX_BLOCK 10000       // number of blocks

#define DIR_ADDRESS 0
#define FREE_LIST_ADDRESS 7
#define FAT_ADDRESS 9000

#define FREE -1
#define USED 0

/* ---------- GLOBAL VARIABLES ---------- */

const char *FILENAME = "sfsfile.dsk";

/* ---------- HELPER FUNCTION PROTOTYPES ---------- */

int read_stream(void *stream, int size, int block);
void write_stream(void *stream, int size, int block);
void write_file(char *stream, int size, int block, int fileID);

/* ---------- DATA STRUCTURES ---------- */

/* * * DIRECTORY TABLE */

struct directory_entry {
	char name[16];    // name of the file - fixed length string of 15 characters (+ null character)
	int size;         // size of the file in bytes
	int date;         // last modification time of the file
	int FAT_index;    // index of the FAT entry that contains points to the first block of the file
};

struct directory_entry directory[MAX_FILES];

/* * * FAT */

// each FAT entry contains the index of a block and that of the next FAT entry for the current file
// FAT[n][0] contains the block corresponding to FAT entry n
// FAT[n][1] contains the index of the next entry - or EOF if no more blocks in the file
int FAT[MAX_BLOCK][2];

/* * * FREE BLOCK LIST */

// ASSUMPTION free block list can contained within a single block

// simple array that indicates whether block i is free or not
// FREE (-1) or USED (0) - defined above
int free_list[MAX_BLOCK];

/* FILE DESCRIPTOR TABLE */

struct fdt_entry {
	int read_ptr;         // current read position in the file (bytes)  - init : 0
	int write_ptr;        // current write position in the file (bytes) - init : size of file or 0
	int directory_index;  // index of the directory entry for this file
};

struct fdt_entry FDT[MAX_FILES];

/* ---------- API FUNCTIONS ---------- */

/* mksfs: initializes the data and the data structures
 if fresh is 0, reall all the data structures from the file
 else create empty data structures and overwrite the ones in the file
 */
int mksfs(int fresh) {
	int i;

	// Compute data structures size
	int size_dir = MAX_FILES * sizeof(struct directory_entry);
	int size_FAT = 2 * MAX_BLOCK * sizeof(int);
	int size_free_list = MAX_BLOCK * sizeof(int);

	if (fresh == 0) {

		// call library emulator function
		if (init_disk((char *)FILENAME, BLOCK_SIZE, MAX_BLOCK) == -1)
			exit(-1);

		// read data structures to memory using helper function read_stream
		read_stream(directory, size_dir, DIR_ADDRESS);  // read disk blocks corresponding to directory and sotre in memory directory
		read_stream(free_list, size_free_list, FREE_LIST_ADDRESS); // read disk block and store in memory free list
		read_stream(FAT, size_FAT, FAT_ADDRESS);         // read disk block for FAT and store in memory FAT

	} else {

		// DATA STRUCTURES
		for (i = 0; i < MAX_FILES; i++) {
			// clear directory
			strcpy(directory[i].name, "");
			directory[i].size = -1;
			directory[i].date = -1;
			directory[i].FAT_index = FREE;

			// clear FDT
			FDT[i].read_ptr = FDT[i].write_ptr = -1;
			FDT[i].directory_index = FREE;
		}

		for (i = 0; i < MAX_BLOCK; i++) {
			// clear free list
			free_list[i] = FREE;

			// clear FAT
			FAT[i][0] = FREE;
			FAT[i][1] = FREE;
		}

		// FILE SYSTEM
		if (init_fresh_disk((char *) FILENAME, BLOCK_SIZE, MAX_BLOCK) == -1)
			exit(-1);

		write_stream(directory, size_dir, DIR_ADDRESS);			// write directory to disk blocks 0-6
		write_stream(free_list, size_free_list, FREE_LIST_ADDRESS);		// write free list to disk blocks 7-46
		write_stream(FAT, size_FAT, FAT_ADDRESS);			// write FAT to disk block

		// Update free list
		for (i = 0; i < 47; i++) free_list[i] = USED;
		for (i = FAT_ADDRESS; i < MAX_BLOCK; i++) free_list[i] = USED;

	}

	return 0;
}

void sfs_ls(void) {

	int i, isEmpty = -1;

  printf("Listing Directory\n"); // new line

	for (i = 0; i < MAX_FILES; i++) {
		if (directory[i].FAT_index!= FREE) {
			printf("%s\t\t%d\t\t%d\t\t%d\n", directory[i].name, directory[i].size, directory[i].FAT_index, directory[i].date);
			isEmpty = 0;
		}
	}

	if (isEmpty) puts("Directory is empty");
}

int sfs_fopen(char *name) {
	int i, j, free_list_index, FAT_index;

	// search for file in current directory
	for (i = 0; i < MAX_FILES; i++) {
		if (!strcmp(directory[i].name, name)) {   // file exists, add FDT entry

			for (j = 0; j < MAX_FILES; j++) {   // find first available cell in array
				if (FDT[j].directory_index == FREE) {
					FDT[j].directory_index = directory[i].FAT_index;
					FDT[j].read_ptr = 0;
					FDT[j].write_ptr = directory[i].size;	// append mode
					return FDT[j].directory_index;
				}
			}
		}
	}

	// if this is line is reached, file does not exist
	// allocate a block of memory for a new file

	// first find a free block
	for (free_list_index = 0; free_list_index < MAX_BLOCK && free_list[free_list_index] == USED; free_list_index++);
	if (free_list_index >= MAX_BLOCK) return -1;   // no free space

	free_list[free_list_index] = USED;  // set block to USED

	// then find a free FAT entry
	for (FAT_index = 0; FAT_index < MAX_BLOCK && FAT[FAT_index][0] != FREE; FAT_index++);
	if (FAT_index >= MAX_BLOCK) return -1;   // no free space

	FAT[FAT_index][0] = free_list_index;  // entry points to allocated block
	FAT[FAT_index][1] = EOF;

	// find a free directory entry
	for (i = 0; i < MAX_FILES && directory[i].size != -1; i++);
	if (i >= MAX_FILES) return -1;   // no free space

	// and initialize file
	strcpy(directory[i].name, name);
	directory[i].size = 0;
	directory[i].date = (int)time(NULL);
	directory[i].FAT_index = FAT_index;

	// find a free entry in FDT
	for (i = 0; i < MAX_FILES && FDT[i].directory_index != FREE; i++);
	if (i >= MAX_FILES) return -1;   // no free space

	// set fdt entry
	FDT[i].directory_index = FAT_index;
	FDT[i].read_ptr = FDT[i].write_ptr = 0;

	return FDT[i].directory_index;
}

int sfs_fclose(int fileID) {
	// find file entry in FDT
	int i;

	for (i = 0; i < MAX_FILES; i++) {
		if (FDT[i].directory_index == fileID) {
			// clear entry
			FDT[i].directory_index = FREE;
			FDT[i].read_ptr = 0;
			FDT[i].write_ptr = 0;

			return 0;
		}
	}

	// entry with direct_index fileID not found
	puts("File not found. Is is open?");

	return -1;
}

/* writes length bytes from buffer buf into the open file at fileID,
 starting from the current write offset
 return : number of bytes written or negative value on error
 */
int sfs_fwrite(int fileID, char *buf, int length) {
	int i, block;

	// find FDT index for fileID
	for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileID; i++);
	directory[fileID].size += length;	// update file size

	// compute last block used
	block = (FDT[i].write_ptr) / BLOCK_SIZE;

	write_file(buf, strlen(buf), block, fileID);

	return 0;
}

int sfs_fread(int fileID, char *buf, int length) {
	int i, block;
	int bytes_read = 0;
	int remainder;

  // make sure fileID is a plausible ID
  if (fileID == -1) return -1;

	// temp buffer can hold one block
	char temp_buf[BLOCK_SIZE] = "";

	// find FDT index for fileID
	for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileID; i++);
	if (i >= MAX_FILES) return -1;

	block = (FDT[i].read_ptr + 1) / BLOCK_SIZE;		 // block containing read pointer
	remainder = abs(BLOCK_SIZE - FDT[i].read_ptr);   // positive remainder in current block

	// read entire current block
	bytes_read += read_blocks(block, 1, temp_buf);

	if (length <= remainder) {    // means that the contents we want to read fits in the remainder of the current block
		memcpy(buf, temp_buf + (FDT[i].read_ptr % BLOCK_SIZE), length);
		FDT[i].read_ptr += length;	// update read pointer
		length = 0;
	} else {
		memcpy(buf, temp_buf + (FDT[i].read_ptr % BLOCK_SIZE), remainder);
		FDT[i].read_ptr += length;	// upate read pointer
		length -= remainder;
	}

	block = FAT[FDT[i].directory_index][1];

	while (block != EOF && length > 0) {
		// read next block
		bytes_read += read_blocks(block, 1, temp_buf);

		if (length > BLOCK_SIZE) {  // read entire block
			memcpy(buf + bytes_read, temp_buf, BLOCK_SIZE);
			length -= BLOCK_SIZE;
			FDT[i].read_ptr += BLOCK_SIZE;
		} else {
			memcpy(buf + bytes_read, temp_buf, length);
			length = 0;
			FDT[i].read_ptr += length;
		}

		// find next block
		block = FAT[FDT[i].directory_index][1];
	}

	return bytes_read;
}

/* sfs_fseek : modifies the read and write pointers
 both pointers are set by a single invokation of the sfs_fseek() function
 NOTE nothing to do on disk
 */
int sfs_fseek(int fileID, int loc) {
	// find file entry in FDT
	int i;

	for (i = 0; i < MAX_FILES; i++) {
		if (FDT[i].directory_index == fileID) {
			// Modify both pointers in memory
			FDT[i].read_ptr = loc;
			FDT[i].write_ptr = loc;
			return 0;
		}
	}

	// entry with direct_index fileID not found
	puts("File not found. Is is open?");

	return -1;
}

int sfs_remove(char *file) {
	int block, i;

	// find file in directory
	for (i = 0; i < MAX_FILES && strcmp(directory[i].name, file); i++) ;

	if (i >= MAX_FILES) return -1; // file not found

	// temporary save FAT_index
	int temp = directory[i].FAT_index;

	// clear directory entry
	strcpy(directory[i].name, "");
	directory[i].size = -1;
	directory[i].date = -1;
	directory[i].FAT_index = FREE;

	while (temp != EOF) {
		block = FAT[temp][0];
		free_list[block] = FREE;  // clear free list entry
		FAT[temp][0] = FREE;      // clear FAT entry
		FAT[temp][1] = EOF;

		temp = FAT[temp][1];
	}

	return 0;
}

/* Helper function to read a number of blocks */
int read_stream(void *stream, int size, int block) {
	int pos = 0;
	int bytes_read = 0;
	char buffer[BLOCK_SIZE];

	while (size > 0) {
		bytes_read += read_blocks(block, 1, buffer);  // read 1 block starting at address block into buffer

		if (size > BLOCK_SIZE)
			memcpy(stream + pos, buffer, BLOCK_SIZE);
		else
			memcpy(stream + pos, buffer, size);

		size -= BLOCK_SIZE;
		pos += BLOCK_SIZE;
		block++;
	}

	return bytes_read;
}

void write_stream(void *stream, int size, int block) {
	char buffer[BLOCK_SIZE];
	int pos = 0;

	for ( ; size > 0; block++) {
		if (size > BLOCK_SIZE)
			memcpy(buffer, stream + pos, BLOCK_SIZE);
		else
			memcpy(buffer, stream + pos, size);

		// use emulator function
		write_blocks(block, 1, buffer);

		size -= BLOCK_SIZE;
		pos += BLOCK_SIZE;
	}
}

void write_file(char *stream, int size, int block, int fileID) {

	int free_list_index, FAT_index;
	int i, j, pos = 0;

	// find FDT entry for fileID
	for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileID; i++) ;

	// find directory entry
	for (j = 0; j < MAX_FILES && directory[j].FAT_index != fileID; j++) ;

	// remainder in last block used by file
	int remainder = BLOCK_SIZE - (FDT[i].write_ptr % BLOCK_SIZE);

	// read last block into buffer
	char buffer[BLOCK_SIZE] = "";
	read_blocks(block, 1, buffer);

	if (size <= remainder) {    // stream can fit in block remainder
		// write
		memcpy(buffer + (FDT[i].write_ptr % BLOCK_SIZE), stream, size);

		// update data structures
		FDT[i].write_ptr += size;
		directory[j].date = time(0);
		size = 0;
	} else {                    // stream doesn't fit in the last block
		// write as much as possible
		memcpy(buffer + (FDT[i].write_ptr % BLOCK_SIZE), stream, remainder);

		// update data structures
		FDT[i].write_ptr += remainder;
		directory[j].date = time(0);

		// save position
		pos = remainder;
	}

	// write block back to disk using emulator function
	write_blocks(block, 1, buffer);

	// we must now write the rest of the stream if needed
	while (size > 0) {

		// find a free block in free_list
		for (free_list_index = 0; free_list_index < MAX_BLOCK && free_list[free_list_index] != FREE; free_list_index++) ;

		free_list[free_list_index] = USED;  // set block to USED

		// find free FAT entry
		for (FAT_index = 0; FAT_index < MAX_BLOCK && FAT[FAT_index][0] != FREE; FAT_index++);

		// Update fat entry
		FAT[block][1] = FAT_index;  // link to next fat entry
		FAT[FAT_index][0]= free_list_index;
		FAT[FAT_index][1] = EOF;
		block = free_list_index;

		// same pattern as above
		if (size <= BLOCK_SIZE) {
			memcpy(buffer, stream + pos, size);
			FDT[i].write_ptr += size;
		} else {  // fill as much as possible
			memcpy(buffer, stream + pos, BLOCK_SIZE);
			FDT[i].write_ptr += BLOCK_SIZE;
		}

		// write back to disk
		write_blocks(block, 1, buffer);

		size -= BLOCK_SIZE;
		pos += BLOCK_SIZE;

		directory[j].date = time(0);

	}

}
