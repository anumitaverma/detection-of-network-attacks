# detection-of-network-attacks
This goal of this project was to differentiate a normal network traffic from an attack network traffic. This project is based on the paper "FFSc: a novel measure for low-rate and high-rate DDoS attack detection using multivariate data analysis" and followed the algorithm presented in this paper. 

Details of the files:
parserregex.py extracts features out of the tcpdump files. 
We have used capinfos to calculate packet rates for each tcpdump.
And then we are extracting total and unique IP addresses, shannon entropy and writing them to csv file.

The inside_csv folder has train, validation and test subfolders. Each of them have network samples in it. Each csv has 4 columns:
total_ip,
unique_ip,
packet_rate,
entropy_ip

We use these files in featurescore.py which implements algorithms 1 and 2 from the paper and calculates dis_BHK values for each of the samples.
