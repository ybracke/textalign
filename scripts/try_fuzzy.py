from fuzzysearch import find_near_matches

f_norm = "tests/testdata/simplicissimus_norm.txt"
with open(f_norm, "r", encoding="utf-8") as f:
    norm = f.read()
    norm = norm * 10

norm = ' '.join([line.split()[0] for line in norm.split("\n") if len(line.split())])

near_matches = find_near_matches('ihre Vettern Eſeltreiber : ihre Bruͤder', norm, max_l_dist=10)
print(near_matches)