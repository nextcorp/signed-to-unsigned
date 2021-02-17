import wave
import struct
import sys

def avg_tbl(t):
    summed = []
    for i in range(0, len(t), 2):
        summed.append(round((t[i]+t[i+1])/2, 0))
    return summed

def unpack_two_ch(struct_val):
    x = (struct_val[0]+struct_val[1])/2
    return round(x, 0)

def get_sample_data(fname):
    print("opening file...")
    f_inp = wave.open(fname, "r")
    fbyte = f_inp.getsampwidth()
    fsamp = f_inp.getframerate()
    flen = f_inp.getnframes()
    file_params = (f_inp.getnframes(), f_inp.getframerate(), f_inp.getnchannels(), f_inp.getsampwidth())
    data = []
    if (file_params[2] == 1):
        get_sample_value = lambda x: struct.unpack("<h", x)[0]
    elif (file_params[2] == 2):
        get_sample_value = lambda x: unpack_two_ch(struct.unpack("<2h", x))
    else:
        exit()
    if (fbyte==1):
        print("getting file data...")
        for i in range(0, flen):
            data.append(int(get_sample_value(f_inp.readframes(1))))
    elif (fbyte==2):
        print("getting file data")
        for i in range(0, flen):
            wdata = int(get_sample_value(f_inp.readframes(1)))
            x = ((wdata/32767)*127)+128
            data.append(int(round(x, 0)))
    else:
        print("error: can't open input file")
        exit()
    return data, fsamp
    
def unsigntosign(inp):
    out = []
    for value in inp:
        out.append(value-128)
    return out
    
def enc(inputfile, outfile):
    samples, samplerate = get_sample_data(inputfile)
    if (samplerate==32000):
        osr = 1
    elif (samplerate==44100):
        osr = 2
    elif (samplerate==48000):
        osr = 3
    else:
        print("unsupported format")
        exit()
    print("file length: ", len(samples), " samples")
    signed_values = unsigntosign(avg_tbl(avg_tbl(samples)))
    outname = outfile
    f_out = open(outname, "wb")
    print("writing output file...")
    f_out.write(struct.pack("3B", 78, 88, 65))
    f_out.write(struct.pack("B", osr))
    for val in signed_values:
        f_out.write(struct.pack("b", int(val)))
    f_out.close()
    print("done")

def signtousign(t):
    t_out = []
    for v in t:
        x = struct.unpack("b", struct.pack("B", v))
        t_out.append(int(x[0])+128)
    return t_out

def dec(inputfile, outfile):
    f_inp = open(str(inputfile), "rb")
    fdata = []
    print("reading file...")
    while True:
        byte = f_inp.read(1)
        if byte:
            x = struct.unpack("B", byte)
            fdata.append(int(x[0]))
        else:
            break
    if ((fdata[0]==78) and (fdata[1]==88) and (fdata[2]==65)):
        print("header detected")
        if (fdata[3] == 1):
            frate = 8000
        elif (fdata[3] == 2):
            frate = 11025
        elif (fdata[3] == 3):
            frate = 12000
        else:
            print("unsupported format")
            exit()
        for i in range(0, 4):
            fdata.pop(i)
        unsigned_values = signtousign(fdata)
        f_out = wave.open(str(outfile), "w")
        f_out.setparams((1, 1, frate, len(unsigned_values), "NONE", "not compressed"))
        print("writing output file...")
        for val in unsigned_values:
            f_out.writeframes(struct.pack("B", int(val)))
        f_out.close()
        print("done")
    else:
        print("cant detect header")
        exit()

def main():
    args = sys.argv
    if (len(args)<3):
        print("usage: signed_unsigned.py <enc/dec> <filename> <filename>")
        print("enc - convert unsigned to signed 8bit")
        print("dec - get wave file from signed 8bit")
    elif (args[1]=="enc"):
        enc(args[2], args[3])
    elif (args[1]=="dec"):
        dec(args[2], args[3])        
main()