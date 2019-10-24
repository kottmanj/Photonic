for division in [0,1,2,3]:
    for randomize in [0,1]:
        for randomize_components in [0,1]:
                if division < 2 and randomize_components == 1:
                    continue
                for trotter_steps in [1,2,4,8]:
                    filename='input_division_'+str(division)+"_randomize_"+str(randomize)+"_steps_"+str(trotter_steps)+"_randomize_components_"+str(randomize_components)
                    with open(filename, 'w+') as file:
                        file.write('division '+str(division))            
                        file.write('\nrandomize '+str(randomize))            
                        file.write('\ntrotter_steps '+str(trotter_steps))
                        file.write('\nrandomize_component_order '+str(randomize_components))
