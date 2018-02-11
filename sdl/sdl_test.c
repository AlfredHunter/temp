#include "SDL.h"
#include "SDL_mutex.h"

#include <stdio.h>

#define SIZE 10

static SDL_atomic_t done;

static int buffer[SIZE];
static int front = 0, rear = 0;

static SDL_sem *full, *empty;
static SDL_mutex *mutex;

static int insertItem(int item)
{
    if ((rear+1)%SIZE == front) return -1;

    buffer[rear] = item;
    rear = (rear+1)%SIZE;

    return 0;
}

static int removeItem(int* item)
{
    if (front == rear) return -1;

    *item = buffer[front];
    front = (front+1)%SIZE;

    return 0;
}

static int produceThread(void *param)
{
    int data = 0;

    while (!SDL_AtomicGet(&done))
    {
        SDL_SemWait(empty);
        SDL_LockMutex(mutex);

        if (!insertItem(data))
        {
            printf("produce an item: %d\r\n", data);
            data++;
        }
        
        SDL_UnlockMutex(mutex);
        SDL_SemPost(full);
        SDL_Delay(200);
    }

    return 0;
}

static int consumerThread(void *param)
{
    int data;

    while (!SDL_AtomicGet(&done))
    {
        SDL_SemWait(full);
        SDL_LockMutex(mutex);
        
        if (!removeItem(&data))
        {
            printf("consumer an item: %d\r\n", data);
        }
        
        SDL_UnlockMutex(mutex);
        SDL_SemPost(empty);
        SDL_Delay(200);
    }

    return 0;
}

int main(int argc, char* argv[])
{
    SDL_Thread *consumer, *produce;
    int thread_ret;

    SDL_AtomicSet(&done, 0);

    mutex = SDL_CreateMutex();
    full = SDL_CreateSemaphore(0);
    empty = SDL_CreateSemaphore(SIZE);

    if (!mutex || !full || !empty)
    {
        printf("couldn't create mutex or semaphore\r\n");
        return -1;
    }

    printf("start test...\r\n");

    produce = SDL_CreateThread(produceThread, "ProduceThread", (void *)NULL);
    consumer = SDL_CreateThread(consumerThread, "ConsumerThread", (void *)NULL);

    if ( !consumer || !produce) {
        printf("create thread failed: %s\r\n", SDL_GetError());
        return -1;
    }

    //SDL_AtomicSet(&done, 1);

    SDL_WaitThread(produce, &thread_ret);
    SDL_WaitThread(consumer, &thread_ret);
    printf("thread failed: %s\r\n", SDL_GetError());

    SDL_DestroySemaphore(full);
    SDL_DestroySemaphore(empty);
    SDL_DestroyMutex(mutex);

    return 0;
}

