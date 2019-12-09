import subprocess, shlex, time

input_command = shlex.split('sudo tcpdump -AUtttvvvXXnns1024 -i lo0 port 9001 -l')
regex = shlex.split('egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr [0-9]+|length [0-9][0-9]|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"')
#regex_obj = re.compile(regex)
#input_command = shlex.split('sudo tcpdump -l -AUtttvvvXXnns1024 -i lo0 port 9001 | egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr ['
                #'\'0-9]+|length [0-9][0-9|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"')


def parse_packet(packet_list):
    delta_time = ''
    val_timestamp = ''
    ecr_timestamp = ''
    src_port = ''
    dest_port = ''
    length = ''
    payload = '0'
    for entry in packet_list:
        p = subprocess.Popen(regex, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8', universal_newlines=False, shell=False)
        out = p.communicate(input=entry)[0]
        if out is not None:
            out = out.split('\n')
            # This block always starts with 127.0.0... ip and is always followed by val and ecr timestamps in order
            if out[0].startswith('127'):
                ip = out[0].split(' > ')
                src = ip[0].split('.')
                src_port = src[4]

                dest = ip[1].split('.')
                dest_port = dest[4]

                val = out[1].split(' ')
                val_timestamp = val[1]

                ecr = out[2].split(' ')
                ecr_timestamp = ecr[1]

            # This block always starts with a delta time (00:00:00...) and followed by length
            elif out[0].startswith('0'):
                temp_timestamp = out[0].split(':')
                temp_timestamp = temp_timestamp[2].split('.')
                delta_time = temp_timestamp[1]

                temp_length = out[1].split(' ')
                length = temp_length[1]

            # This block should contain only the payload
            elif out[0].startswith('3'):
                hex_payload = out[0].replace(' ', '')
                payload = int(hex_payload, 16)

        # If no payload block was found, make it 0. Payload block is always the last line
        else:
            payload = '0'

    parsed_packet = [length, delta_time, src_port, dest_port, payload, val_timestamp, ecr_timestamp]
    for i in parsed_packet:
        print(i)
    return parsed_packet


packet = []
line_count = 0
p = subprocess.Popen(input_command, stdout=subprocess.PIPE, universal_newlines=False)
time.sleep(5)
for row in iter(p.stdout.readline, b''):
    new_row = row.rstrip().decode('utf-8')
    packet.append(new_row)
    line_count += 1
    if line_count == 6:
        processed_packet = parse_packet(packet)
        line_count = 0
        packet.clear()
