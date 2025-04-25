import json
import itertools

def load_input(file='input.json'):
    with open(file, 'r') as f:
        return json.load(f)

def binary_to_indices(bits):
    return int(bits.replace('x', '0'), 2)

def get_minterms_and_dontcares(data, inputs):
    minterms = []
    dontcares = []
    for row in data:
        bits = ''.join(str(row[i]) for i in inputs)
        if row['Y'] == '1':
            minterms.append(bits)
        elif row['Y'].lower() in ['x', 'X']:
            dontcares.append(bits)
    return minterms, dontcares

def group_by_ones(terms):
    groups = {}
    for term in terms:
        ones = term.count('1')
        groups.setdefault(ones, []).append(term)
    return groups

def combine_terms(a, b):
    diff = 0
    combined = ''
    for x, y in zip(a, b):
        if x != y:
            diff += 1
            combined += '-'
        else:
            combined += x
    return combined if diff == 1 else None

def get_prime_implicants(terms):
    terms = list(set(terms))
    checked = set()
    prime_implicants = set()
    while True:
        next_terms = set()
        combined_any = False
        for i in range(len(terms)):
            for j in range(i+1, len(terms)):
                combined = combine_terms(terms[i], terms[j])
                if combined:
                    next_terms.add(combined)
                    checked.add(terms[i])
                    checked.add(terms[j])
                    combined_any = True
        for term in terms:
            if term not in checked:
                prime_implicants.add(term)
        if not combined_any:
            break
        terms = list(next_terms)
        checked.clear()
    return list(prime_implicants)

def get_covered_terms(implicant, num_inputs):
    wildcards = [pos for pos, char in enumerate(implicant) if char == '-']
    fixed = list(implicant)
    combos = []
    for bits in itertools.product('01', repeat=len(wildcards)):
        for i, b in zip(wildcards, bits):
            fixed[i] = b
        combos.append(''.join(fixed))
    return combos

def get_essential_prime_implicants(prime_implicants, minterms):
    cover_table = {}
    for m in minterms:
        cover_table[m] = []
        for p in prime_implicants:
            if m in get_covered_terms(p, len(m)):
                cover_table[m].append(p)

    epi = set()
    for m, covers in cover_table.items():
        if len(covers) == 1:
            epi.add(covers[0])
    return list(epi)

def term_to_expression(term, inputs):
    expr = ''
    for bit, var in zip(term, inputs):
        if bit == '1':
            expr += var
        elif bit == '0':
            expr += var + "'"
    return expr

def generate_netlist(terms, inputs):
    netlist = []
    and_count = 0
    or_inputs = []
    for term in terms:
        literals = []
        for bit, var in zip(term, inputs):
            if bit == '1':
                literals.append(var)
            elif bit == '0':
                literals.append(f"NOT({var})")
        if len(literals) == 1:
            netlist.append(f"w{and_count} = {literals[0]}")
        else:
            netlist.append(f"w{and_count} = AND({', '.join(literals)})")
        or_inputs.append(f"w{and_count}")
        and_count += 1
    netlist.append(f"Y = OR({', '.join(or_inputs)})")
    return netlist

def simulate(terms, inputs):
    results = []
    for values in itertools.product([0, 1], repeat=len(inputs)):
        val_dict = dict(zip(inputs, values))
        result = 0
        for term in terms:
            term_result = 1
            for bit, var in zip(term, inputs):
                if bit == '1':
                    term_result &= val_dict[var]
                elif bit == '0':
                    term_result &= not val_dict[var]
            result |= term_result
        results.append((val_dict, result))
    return results

def main():
    input_data = load_input()
    inputs = input_data[0].keys() - {'Y'}
    inputs = sorted(inputs)  # ensure consistent order
    minterms, dontcares = get_minterms_and_dontcares(input_data, inputs)

    all_terms = minterms + dontcares
    prime_implicants = get_prime_implicants(all_terms)
    essential_implicants = get_essential_prime_implicants(prime_implicants, minterms)

    final_terms = essential_implicants  # simplification could go further
    expression = ' + '.join([term_to_expression(t, inputs) for t in final_terms])
    netlist = generate_netlist(final_terms, inputs)
    sim_results = simulate(final_terms, inputs)

    # Write all results
    with open("output.txt", "w") as f:
        f.write("Inputs: " + ', '.join(inputs) + "\n\n")
        f.write("Minterms (Y=1):\n" + '\n'.join(minterms) + "\n\n")
        f.write("Don't Cares (Y=x):\n" + '\n'.join(dontcares) + "\n\n")
        f.write("Prime Implicants:\n" + '\n'.join(prime_implicants) + "\n\n")
        f.write("Essential Prime Implicants:\n" + '\n'.join(essential_implicants) + "\n\n")
        f.write("Final SOP Expression:\n" + expression + "\n\n")
        f.write("Gate-Level Netlist:\n" + '\n'.join(netlist) + "\n\n")
        f.write("Simulation Results:\n")
        for row, out in sim_results:
            bits = ' '.join([f"{k}={v}" for k, v in row.items()])
            f.write(f"{bits} => Y={int(out)}\n")

if __name__ == "__main__":
    main()
