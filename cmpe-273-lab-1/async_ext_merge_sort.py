import os
from itertools import islice
from heapq import heapify, heappush, heappop
import time
import asyncio

class node:
 
    def __init__(self, val, index, file):
        self.value = val
        self.fileIndex = index
        self.fileName =file
 
    def __lt__(self, nxt):
        return self.value < nxt.value

def file_merge_sort(list):
    if len(list) > 1:
        mid = int(len(list)/2)
        leftArray = list[mid:]
        rightArray = list[:mid]
        file_merge_sort(leftArray)
        file_merge_sort(rightArray)
        lIndex = 0
        rIndex = 0
        index = 0
        while (lIndex < len(leftArray) and rIndex < len(rightArray)):
            if (leftArray[lIndex] <= rightArray[rIndex]):
                list[index] = leftArray[lIndex]
                lIndex += 1
            
            else:
                list[index] = rightArray[rIndex]
                rIndex += 1

            index += 1
        
        while (lIndex < len(leftArray)):
            list[index] = leftArray[lIndex]
            lIndex += 1
            index += 1
        
        while (rIndex < len(rightArray)):
            list[index] = rightArray[rIndex]
            rIndex += 1
            index += 1

async def sort_file(inputPath, file, chunkPath, chunkCount):
    with open(inputPath+"/"+str(file)) as f:
        chunkList = []
        for line in f:
            line = line.split("\n")
            chunkList.append(int(line[0]))
        chunkFile = open((chunkPath + '/chunk_' + str(chunkCount)) + '.txt','w+')
        file_merge_sort(chunkList)
        for chunk in chunkList:
            chunkFile.write("%i\n" % chunk)
        chunkFile.close()

async def main():

    inputPath = 'input'

    chunkPath = 'chunks'

    outputPath = 'output'

    inputFiles = os.listdir(inputPath)

    chunkCount = 1

    threads = list()

    for file in inputFiles:
        thread = sort_file(inputPath, file, chunkPath, chunkCount)
        chunkCount += 1
        threads.append(thread)
    await asyncio.gather(*threads)

    chunkFiles = os.listdir(chunkPath)

    heap = []
    heapify(heap)

    for file in chunkFiles:
        with open(chunkPath+"/"+str(file)) as chunkFile:
            num = chunkFile.readline()
            
            heappush(heap, node(int(num), 0, str(file)))

    heapify(heap)

    outputFile = open(outputPath + '/sorted.txt', 'w+')

    while (len(heap) > 0):
        currNode = heappop(heap)
        outputFile.write(str(currNode.value)+'\n')
        chunkName = currNode.fileName
        chunkFile = open(str(chunkPath)+"/"+str(chunkName))

        lines = chunkFile.readlines()

        if (currNode.fileIndex+1 == len(lines)):
            continue

        num = lines[currNode.fileIndex+1].split('\n')
        
        if (num[0] != ''):
            heappush(heap, node(int(num[0]), currNode.fileIndex+1, chunkName))

    outputFile.close()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())