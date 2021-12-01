# Photonic

Illustrative examples for the optimization of photonic setups with digital quantum computers  
Following this [article](https://iopscience.iop.org/article/10.1088/2058-9565/abfc94/meta) ([ArXiv:2006.03075](https://arxiv.org/abs/2006.03075)).  

The calculations from the article can be found under examples.  

In [slides.pdf](slides.pdf) you can find the slides of a presentation about the topic.  

# Dependencies
You will need the `tequila` package  
[get it here](https://github.com/tequilahub/tequila)

Otherwise it will be automatically installed when you run  
`pip install . `
or, for developer mode:  
`pip install -e . `  

If you use Windows or Max OS you might run into trouble here.   
See the [tequila](https://github.com/tequiahub/tequila) repo for more information.

There is however no installation necessary:  
In order to use the code, it suffices to add the path to photonic to your PYTHONPATH  
`export PYTHONPATH=$PYTHONPATH:/path/to/photonic`  

We recommend to use [qulacs](https://github.com/qulacs) as quantum backend within `tequila`.  
Just install and it will be selected automatically:
```bash
pip install qulacs
```

# Trouble, Comments or Ideas?  
Please let us know over github or email (see arxiv link above or [here](https://www.matter.toronto.edu/people#PostDocs) ) :-)

