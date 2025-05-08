Changes
- Fix MRCA changes in avida-empirical (to now propertly work with a non-rooted population)
- Keeping preference for replacing oldest/merit
  - ACTUALLY, gen-sub.py was not setting this as expected (still had random replacement)
- InjectAll instead of inject single to start population at capacity.
- Reduce task rewards

Learned:
- Effect of spatial structure depends on reward level
  - (tracks with chemical ecology results)
