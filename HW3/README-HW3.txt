Following are the major adjustments made for the exercise:

1)
In hw2_utils (which is now hw3_utils), the structure of TraceEntry has changed
in order to reflect the required output of this exercise.
Take these changes into account and modify your code from HW2 accordingly if you
wish to use it in this exercise:

	* There is now a temperature field which
	  you should set in your implementation before printing the object.

	* The printing format (defined in __str__) was changed to match the expected output.
	  The delta and hit fields are no longer printed, and have been replaced by
	  the temperature field.

2)
The code no longer loads all accesses into memory in advance:
each access is now read in turn from the input file and loaded/split by itself.

3)
The no-trace argument is now gone since the output is different:
Instead of printing the final hitrate line, the code outputs a full file as in the output format
section of the pdf

note that for this exercise your code should run with a different command than the supplied paging-policy.py template or your previous HW2 code.

4)
The script "partition_hist" is a new utility script that you can use in order to receive a histogram
that counts the number of SSD blocks in each partition in the simulation.
The script should be passed a single argument that is a path to an XML output file generated 
by the SSD simulator:
./partition_hist <path_to_xml>
