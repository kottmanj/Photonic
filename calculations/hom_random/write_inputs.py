counter = 0
for S in [0,1]:
	for qpm in [2,3]:
		for randomize in [0,1]:
			for trotter_steps in [1,2,5]:
				filename='input_'+str(counter)
				with open(filename, 'w+') as file:
					file.write('S '+str(S))			
					file.write('\nqpm '+str(qpm))			
					file.write('\nrandomize '+str(randomize))			
					file.write('\ntrotter_steps '+str(trotter_steps))	
				counter += 1		
