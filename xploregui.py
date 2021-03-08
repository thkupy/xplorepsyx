#!/usr/bin/python3
# -*- coding: utf-8 -*-

#for simpleaudio on linux the following dependencies have to be met:
#sudo apt-get install -y python3-dev libasound2-dev
import tkinter as tk
from tkinter import ttk
from functools import partial
import time
import math
import datetime
import simpleaudio as sa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.signal as sig


#----------------------------GUI DEFINITIONS-----------------------------------
class Preparewindow:
    def __init__(self, master):
        self.master = master
        self.master.geometry("800x400")
        self.master.grid()
        self.master.grid_rowconfigure(0,weight=1)
        self.master.grid_columnconfigure(0,weight=1)
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="NSEW")
        for row in range(10):
            self.frame.grid_rowconfigure(row, weight=1)
        for col in range(10):
            self.frame.grid_columnconfigure(col, weight=1)
        self.button1 = tk.Button(self.frame, text="Run Exp", command=self.runexp)
        self.button1.grid(row=0, column=0, sticky="NSEW")
        self.button2 = tk.Button(self.frame, text="Test Loudness", command=self.teststim)
        self.button2.grid(row=7, column=0, sticky="NSEW")
        exptext = (
            "Set speaker loudness so that noise and tone are loud " + 
            "but not painful (be careful! this is maximal level!)"
        )
        self.lLoudnessExplanation = tk.Label(self.frame, text=exptext)
        self.lLoudnessExplanation.grid(row=8, column=0, columnspan=5, sticky="NSEW")
        #---
        self.lTonset = tk.Label(self.frame, text="Target onset (ms)")
        self.lTonset.grid(row=1, column=1, sticky="NSEW")        
        self.vTonset = tk.StringVar(value="102")
        self.eTonset = tk.Entry(self.frame, textvariable=self.vTonset)
        self.eTonset.grid(row=1, column=2, sticky="NSEW")
        #---
        self.lTdur = tk.Label(self.frame, text="Target duration (ms)")
        self.lTdur.grid(row=2, column=1, sticky="NSEW")        
        self.vTdur = tk.StringVar(value="25")
        self.eTdur = tk.Entry(self.frame, textvariable=self.vTdur)
        self.eTdur.grid(row=2, column=2, sticky="NSEW")
        #---
        self.lTfreq = tk.Label(self.frame, text="Target frequency (Hz)")
        self.lTfreq.grid(row=3, column=1, sticky="NSEW")        
        self.vTfreq = tk.StringVar(value="2000")
        self.eTfreq = tk.Entry(self.frame, textvariable=self.vTfreq)
        self.eTfreq.grid(row=3, column=2, sticky="NSEW")
        #---
        self.lTatten = tk.Label(self.frame, text="Target attenuation (dB SPL)")
        self.lTatten.grid(row=4, column=1, sticky="NSEW")        
        self.vTatten = tk.StringVar(value="40")
        self.eTatten = tk.Entry(self.frame, textvariable=self.vTatten)
        self.eTatten.grid(row=4, column=2, sticky="NSEW")
        #---
        self.vToggletext = tk.StringVar()
        self.vToggletext.set("Vary Target Level")
        self.vtogglevary = 0
        self.btogglevary = tk.Button(
            self.frame,
            textvariable=self.vToggletext,
            relief="raised",
            command=self.togglevary,
        )
        self.btogglevary.grid(row=5, column=1, sticky="NSEW")
        self.button3 = tk.Button(self.frame, text="Draw Stim", command=self.drawstim)
        self.button3.grid(row=6, column=1, sticky="NSEW")
        #--
        self.lMstyle = tk.Label(self.frame, text="Masker Type")
        self.lMstyle.grid(row=0, column=3, sticky="NSEW")        
        self.vMstyle = tk.StringVar()
        self.cMstyle = ttk.Combobox(
            self.frame,
            textvariable=self.vMstyle,
            state="readonly",
            values=("No Masker", "Tone", "Broadband Noise", "Notched Noise"),
        )
        self.cMstyle.bind("<<ComboboxSelected>>", self.Mstyleupdate)
        self.cMstyle.grid(row=0, column=4, sticky="NSEW")
        self.cMstyle.current(2)
        #---
        self.vMfreq1label = tk.StringVar()
        self.vMfreq1label.set("Masker LF cutoff (Hz)")
        self.lMfreq1 = tk.Label(self.frame, textvariable=self.vMfreq1label)
        self.lMfreq1.grid(row=1, column=3, sticky="NSEW")        
        self.vMfreq1 = tk.StringVar(value="200")
        self.eMfreq1 = tk.Entry(self.frame, textvariable=self.vMfreq1)
        self.eMfreq1.grid(row=1, column=4, sticky="NSEW")
        #---
        self.lMfreq2 = tk.Label(self.frame, text="Masker HF cutoff (Hz)")
        self.lMfreq2.grid(row=2, column=3, sticky="NSEW")        
        self.vMfreq2 = tk.StringVar(value="20000")
        self.eMfreq2 = tk.Entry(self.frame, textvariable=self.vMfreq2)
        self.eMfreq2.grid(row=2, column=4, sticky="NSEW")
        #---
        self.lMfreq3 = tk.Label(self.frame, text="Notch LF cutoff (Hz)")
        self.lMfreq3.grid(row=3, column=3, sticky="NSEW")        
        self.vMfreq3 = tk.StringVar(value="1000")
        self.eMfreq3 = tk.Entry(self.frame, textvariable=self.vMfreq3)
        self.eMfreq3.grid(row=3, column=4, sticky="NSEW")
        #---
        self.lMfreq4 = tk.Label(self.frame, text="Notch HF cutoff (Hz)")
        self.lMfreq4.grid(row=4, column=3, sticky="NSEW")        
        self.vMfreq4 = tk.StringVar(value="3000")
        self.eMfreq4 = tk.Entry(self.frame, textvariable=self.vMfreq4)
        self.eMfreq4.grid(row=4, column=4, sticky="NSEW")
        #---
        self.lMonset = tk.Label(self.frame, text="Masker onset (ms)")
        self.lMonset.grid(row=5, column=3, sticky="NSEW")        
        self.vMonset = tk.StringVar(value="0")
        self.eMonset = tk.Entry(self.frame, textvariable=self.vMonset)
        self.eMonset.grid(row=5, column=4, sticky="NSEW")
        #---
        self.lMdur = tk.Label(self.frame, text="Masker duration (ms)")
        self.lMdur.grid(row=6, column=3, sticky="NSEW")        
        self.vMdur = tk.StringVar(value="100")
        self.eMdur = tk.Entry(self.frame, textvariable=self.vMdur)
        self.eMdur.grid(row=6, column=4, sticky="NSEW")
        #---
        self.lMatten = tk.Label(self.frame, text="Masker attenuation (dB)")
        self.lMatten.grid(row=7, column=3, sticky="NSEW")        
        self.vMatten = tk.StringVar(value="10")
        self.eMatten = tk.Entry(self.frame, textvariable=self.vMatten)
        self.eMatten.grid(row=7, column=4, sticky="NSEW")
        self.eMfreq3["state"] = "disabled"#per default we start with the bbn masker
        self.eMfreq4["state"] = "disabled"#per default we start with the bbn masker
    
    def togglevary(self):
        if self.vtogglevary == 0:#...then change to 1
            self.vtogglevary = 1
            self.btogglevary.config(relief="sunken")
            self.vToggletext.set("Vary Masker Level")
        else:
            self.vtogglevary = 0
            self.btogglevary.config(relief="raised")
            self.vToggletext.set("Vary Target Level")
    
    def Mstyleupdate(self, event):
        if self.cMstyle.current() == 0:
            self.eMonset["state"] = "disabled"
            self.eMdur["state"] = "disabled"
            self.eMatten["state"] = "disabled"
            self.eMfreq1["state"] = "disabled"
            self.eMfreq2["state"] = "disabled"
            self.eMfreq3["state"] = "disabled"
            self.eMfreq4["state"] = "disabled"
        elif self.cMstyle.current() == 1:
            self.eMonset["state"] = "normal"
            self.eMdur["state"] = "normal"
            self.eMatten["state"] = "normal"
            self.vMfreq1label.set("Tone Frequency (Hz)")
            self.eMfreq1["state"] = "normal"
            self.eMfreq2["state"] = "disabled"
            self.eMfreq3["state"] = "disabled"
            self.eMfreq4["state"] = "disabled"
        elif self.cMstyle.current() == 2:
            self.eMonset["state"] = "normal"
            self.eMdur["state"] = "normal"
            self.eMatten["state"] = "normal"
            self.vMfreq1label.set("Masker LF cutoff (Hz)")
            self.eMfreq1["state"] = "normal"
            self.eMfreq2["state"] = "normal"
            self.eMfreq3["state"] = "disabled"
            self.eMfreq4["state"] = "disabled"
        else:
            self.eMonset["state"] = "normal"
            self.eMdur["state"] = "normal"
            self.eMatten["state"] = "normal"
            self.vMfreq1label.set("Masker LF cutoff (Hz)")
            self.eMfreq1["state"] = "normal"
            self.eMfreq2["state"] = "normal"
            self.eMfreq3["state"] = "normal"
            self.eMfreq4["state"] = "normal"

    def drawstim(self):
        if self.vtogglevary == 0:
            att = float(self.vTatten.get())
        else:
            att = float(self.vMatten.get())
        testset = {
            "Vary_Masker": bool(self.vtogglevary),
            "Tonset_ms": float(self.vTonset.get()),
            "Tdur_ms": float(self.vTdur.get()),
            "Tfreq_Hz": float(self.vTfreq.get()),
            "Tatten_dB": float(self.vTatten.get()),
            "Mstyle_str": self.vMstyle.get(),
            "Mstyle_int": self.cMstyle.current(),
            "Mfreq1_Hz": float(self.vMfreq1.get()),
            "Mfreq2_Hz": float(self.vMfreq2.get()),
            "Mfreq3_Hz": float(self.vMfreq3.get()),
            "Mfreq4_Hz": float(self.vMfreq4.get()),
            "Monset_ms": float(self.vMonset.get()),
            "Mdur_ms": float(self.vMdur.get()),
            "Matten_dB": float(self.vMatten.get()),
        }
        print(att)
        A = provideaudio(testset, att, True)
        sample_rate = 44100#hardcoded should be exposed to user at some point
        maxdur_ms = np.max((
            testset["Monset_ms"] + testset["Mdur_ms"],
            testset["Tonset_ms"] + testset["Tdur_ms"],
        ))
        stimstart = testset["Tonset_ms"] / 1000.0
        stimdur = testset["Tdur_ms"] / 1000.0
        maskstart = testset["Monset_ms"] / 1000.0
        maskdur = testset["Mdur_ms"] / 1000.0
        maxdur_s = maxdur_ms / 1000.0
        fh = plt.figure()
        sh1 = fh.add_subplot(2,1,1)
        tax = np.linspace(0, maxdur_s, A["aud1"].size)
        sh1.add_patch(patches.Rectangle((maskstart, -1), maskdur, 2, color="r"))
        sh1.add_patch(patches.Rectangle((stimstart, -1), stimdur, 2, color="g"))
        sh1.plot(tax,A["aud1"],"k", linewidth=1)
        #
        N = A["aud1"].size
        dt = 1.0 / sample_rate
        segment_size = np.int32(0.5*N) # Segment size = 50 % of data length
        overlap_fac = 0.97#0.97
        overlap_size = overlap_fac*segment_size
        f, Pxx = sig.welch(
            A["aud1"],
            sample_rate,
            nperseg=segment_size,
            noverlap=overlap_size,
            detrend=False,
        )
        sh2 = fh.add_subplot(2,1,2)
        #sh2.semilogy(f, Pxx)
        Pxx = Pxx / np.max(Pxx)
        sh2.plot(f, 10*np.log10(Pxx))
        sh2.set_xlabel("Frequency (Hz)")
        sh2.set_ylabel("PSD (dB)")
        #
        plt.show()
        
    def teststim(self):
        testset = {
            "Vary_Masker": 0,
            "Tonset_ms": 200.0,
            "Tdur_ms": 125.0,
            "Tfreq_Hz": 1000.0,
            "Tatten_dB": 0.0,
            "Mstyle_str": "None",
            "Mstyle_int": 2,
            "Mfreq1_Hz": 100.0,
            "Mfreq2_Hz": 20000.0,
            "Mfreq3_Hz": 3000.0,
            "Mfreq4_Hz": 4000.0,
            "Monset_ms": 0.0,
            "Mdur_ms": 125.0,
            "Matten_dB": 0.0,
        }
        A = provideaudio(testset, 0.0, True)
        play_obj = sa.play_buffer(A["aud1"], 1, 2, 44100)
        play_obj.wait_done()

    def runexp(self):
        self.app = Experimentwindow(self)


class Experimentwindow:
    def __init__(self, parent):
        self.parent = parent
        self.master = tk.Toplevel(parent.master)
        self.master.geometry("600x250")
        self.master.grid()
        self.master.grid_rowconfigure(0,weight=1)
        self.master.grid_columnconfigure(0,weight=1)
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="NSEW")
       # FRAME Grid
        for row in range(3):
            self.frame.grid_rowconfigure(row, weight=1)
        for col in range(4):
            self.frame.grid_columnconfigure(col, weight=1)
        self.ab1 = tk.Button(
            self.frame, text="1", bg="white",
            state = "disabled",
            height=5, width=10, command=partial(self.answer,1),
        )
        self.ab1.grid(column=1, row=1,sticky="NSEW")
        self.ab2 = tk.Button(
        self.frame, text="2", bg="white",
            state = "disabled",
            height=5, width=10, command=partial(self.answer,2),
        )
        self.ab2.grid(column=2, row=1,sticky="NSEW")
        self.ab3 = tk.Button(
            self.frame, text="3", bg="white",
            state = "disabled",
            height=5, width=10, command=partial(self.answer,3),
        )
        self.ab3.grid(column=3, row=1,sticky="NSEW")
        self.gobuttonh = tk.Button(
            self.frame, text="GO", command=self.runonce,
        )
        self.gobuttonh.grid(column=0, row=0,sticky="NSEW")
        self.quitButton = tk.Button(
            self.frame, text = "Quit", command = self.close_windows,
        )
        self.quitButton.grid(column=4, row=2,sticky="NSEW")
        #
        #The number of reversals determins in this simple version the
        #duration of the experiment and the precision of the result (try 10-12)
        self.reversalthreshold = 10 #this should be exposed to the user one day
        self.correctanswer = -1
        self.nreversals = 0
        self.currentstepsize = 8
        self.lastresult = -1
        self.nsameresult = 0
        if self.parent.vtogglevary == 0:
            self.currentattenuation = float(self.parent.vTatten.get())
        else:
            self.currentattenuation = float(self.parent.vMatten.get())
        self.allattenuation = []
        self.allanswers = []
        self.alldelays = []
        self.time_a = 0
        self.stimulusset = {
            "Vary_Masker": bool(self.parent.vtogglevary),
            "Tonset_ms": float(self.parent.vTonset.get()),
            "Tdur_ms": float(self.parent.vTdur.get()),
            "Tfreq_Hz": float(self.parent.vTfreq.get()),
            "Tatten_dB": float(self.parent.vTatten.get()),
            "Mstyle_str": self.parent.vMstyle.get(),
            "Mstyle_int": self.parent.cMstyle.current(),
            "Mfreq1_Hz": float(self.parent.vMfreq1.get()),
            "Mfreq2_Hz": float(self.parent.vMfreq2.get()),
            "Mfreq3_Hz": float(self.parent.vMfreq3.get()),
            "Mfreq4_Hz": float(self.parent.vMfreq4.get()),
            "Monset_ms": float(self.parent.vMonset.get()),
            "Mdur_ms": float(self.parent.vMdur.get()),
            "Matten_dB": float(self.parent.vMatten.get()),
        }

    def runonce(self):
        """
        TODO: here we need some "proper" handling of the stimulus settings and
        the generation of the stimuli.
        """
        #
        print(str(self.currentattenuation))
        A = provideaudio(
            self.stimulusset,
            self.currentattenuation,
        )
        self.correctanswer = A["correctanswer"]
        self.allattenuation.append(self.currentattenuation)
        #
        self.gobuttonh["state"] = "disabled"
        #1111111111111111111111111111111111111
        time.sleep(1)
        self.ab1.configure(bg="yellow")
        self.master.update()
        play_obj = sa.play_buffer(A["aud1"], 1, 2, 44100)
        play_obj.wait_done()
        self.ab1.configure(bg="white")
        self.master.update()
        #222222222222222222222222222222222222
        time.sleep(1)
        self.ab2.configure(bg="yellow")
        self.master.update()
        play_obj = sa.play_buffer(A["aud2"], 1, 2, 44100)
        play_obj.wait_done()
        self.ab2.configure(bg="white")
        self.master.update()
        #3333333333333333333333333333333
        time.sleep(1)
        self.ab3.configure(bg="yellow")
        self.master.update()
        play_obj = sa.play_buffer(A["aud3"], 1, 2, 44100)
        play_obj.wait_done()
        self.ab3.configure(bg="white")
        self.master.update()
        self.ab1["state"] = "normal"
        self.ab2["state"] = "normal"
        self.ab3["state"] = "normal"
        self.time_a = datetime.datetime.now()


    def answer(self, whichbutton):
        time_b = datetime.datetime.now()
        time_delta = time_b - self.time_a
        self.alldelays.append(int(time_delta.total_seconds() * 1000))
        print("ANSWER " + str(whichbutton))
        self.ab1["state"] = "disabled"
        self.ab2["state"] = "disabled"
        self.ab3["state"] = "disabled"
        if whichbutton == self.correctanswer: #a correct answer
            print("DEBUG MESSAGE: correct answer")
            self.allanswers.append(1)
            if self.lastresult == 1:# >1 corrects in a row
                self.nsameresult += 1
                if self.nsameresult >= 4:
                    if self.currentstepsize < 8:
                        self.nsameresult = 0
                        self.currentstepsize *= 2
            elif self.lastresult == 0:#a positive reversal
                self.nsameresult = 0
                self.nreversals += 1
                if self.currentstepsize > 1:
                    self.currentstepsize *= 0.5
            self.lastresult = 1
            if self.parent.vtogglevary == 0:
                """
                The target level is varied. Thus, a correct answer will cause
                the attenaution to increase
                """
                self.currentattenuation += self.currentstepsize#attenuation is increased
            else:
                """
                The masker level is varied. Thus, a correct answer will cause
                the attenaution to decrease
                """
                self.currentattenuation -= self.currentstepsize#attenuation is increased
                if self.currentattenuation < 0.0:
                    self.currentattenuation = 0.0
                    print("MINIMUM ATTENUATION REACHED!! CHECK STIMULUS DESIGN!")
        else:#a wrong answer
            print("DEBUG MESSAGE: wrong answer")
            print("DEBUG MESSAGE: expected answer " + str(self.correctanswer))
            self.allanswers.append(0)
            if self.lastresult == 1:# we have a negative reversal
                self.nreversals += 1
                if self.currentstepsize > 1:
                    self.currentstepsize *= 0.5
            elif self.lastresult == 0:# >1 wrong in a row
                self.nsameresult += 1
                if self.nsameresult >= 4:
                    if self.currentstepsize < 8:
                        self.nsameresult = 0
                        self.currentstepsize *= 2
            self.lastresult = 0
            if self.parent.vtogglevary == 0:
                """
                Logic as above just reversed.
                """
                self.currentattenuation -= self.currentstepsize#attenuation is reduced
                if self.currentattenuation < 0.0:
                    self.currentattenuation = 0.0
                    print("MINIMUM ATTENUATION REACHED!! CHECK STIMULUS DESIGN!")
            else:
                self.currentattenuation += self.currentstepsize#attenuation is increased
        if self.nreversals > self.reversalthreshold:
            self.finalizeexp()
        else:
            self.runonce()
        """
        we now call runonce again. in this case we should set the proper
        variables (see end of init). if the logic above decides that the 
        convergence point was reached, we do not run again. instead we call
        the finalize function which presents results, handles data saving and
        then closes the window.
        """

    def resetexp(self):
        self.gobuttonh["state"] = "normal"

    def finalizeexp(self):
        self.close_windows()
        fh = plt.figure()
        sh1 = plt.subplot(111)
        ansmask = np.array(self.allanswers, dtype="bool")
        result = np.array(self.allattenuation)*-1
        X = np.arange(result.size) + 1 
        plt.plot(X, result, "k-")
        plt.plot(X[np.invert(ansmask)], result[np.invert(ansmask)], "ro")
        plt.plot(X[ansmask], result[ansmask], "go")
        meanlast5 = np.mean(result[-5:])
        stdlast5 = np.std(result[-5:])
        plt.plot((X[-5], X[-1]), (meanlast5, meanlast5),"m-")
        plt.plot((X[-3], X[-3]), (meanlast5 - stdlast5, meanlast5 + stdlast5), "m-")
        if self.parent.vtogglevary == 0:
            thrtext = "Target threshold: "
        else:
            thrtext = "Masker threshold: "
        plt.title(thrtext + str(meanlast5) + "+/-" + str(round(stdlast5,2)))
        plt.show()

    def close_windows(self):
        self.master.destroy()
#----------------------------END OF GUI DEFINITIONS----------------------------


#----------------------AUDIO HELPER FUNCTIONS----------------------------------
def butter_bandstop(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = sig.butter(order, [low, high], btype="bandstop", output="sos")
    return sos


def butter_bandstop_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandstop(lowcut, highcut, fs, order=order)
    y = sig.sosfiltfilt(sos, data)
    return y


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = sig.butter(order, [low, high], btype="bandpass", output="sos")
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sig.sosfiltfilt(sos, data)
    return y


def provideaudio(stim, att, force1=False):
    """
    This function provides the audio stimuli. It will read the stimulusset
    defined by the gui and produce audio snippets, one with the target and
    2 without. If a masker is defined, all three will have the masker.
    The function returns the 3 audio snips in random order and will also return
    an integer that says which audio contains the target.
    """
    sample_rate = 44100#hardcoded should be exposed to user at some point
    maxdur_ms = np.max(
        (stim["Monset_ms"] + stim["Mdur_ms"], stim["Tonset_ms"] + stim["Tdur_ms"])
    )
    maxdur_s = maxdur_ms/1000.0
    Mdur_s = stim["Mdur_ms"]/1000.0
    Tdur_s = stim["Tdur_ms"]/1000.0
    Monset_s = stim["Monset_ms"]/1000.0
    Tonset_s = stim["Tonset_ms"]/1000.0
    Mend_ms = stim["Monset_ms"] + stim["Mdur_ms"]
    Mend_s = Mend_ms/1000.0
    Tend_ms = stim["Tonset_ms"] + stim["Tdur_ms"]
    Tend_s = Tend_ms/1000.0
    #
    if stim["Vary_Masker"]:
        matt = att
        tatt = stim["Tatten_dB"]
    else:
        matt = stim["Matten_dB"]
        tatt = att
    #
    #generate ramp waveform
    rampdur = 0.002#hardcoded should be exposed to user at some point
    on = np.sin(np.linspace(0,0.5*np.pi,int(round(rampdur*sample_rate))))
    #
    #1.generate masker (this can be silence, tone, bb-noise or notched noise
    if stim["Mstyle_int"] == 0:
        print("DEBUG: Silent masker")
        masker = np.zeros((int(round(maxdur_s * sample_rate)),))#maxdur_s of silence
    else:
        if stim["Mstyle_int"] == 1:
            print("DEBUG: Tone masker")
            t = np.linspace(0, Mdur_s, int(round(Mdur_s * sample_rate)), False)
            masker = np.sin(stim["Mfreq1_Hz"] * t * 2 * np.pi)
        elif stim["Mstyle_int"] == 2:
            print("DEBUG: BBN masker")
            masker=np.random.uniform(
                low=-1.0,
                high=1.0,
                size=int(round(Mdur_s * sample_rate)),
            )
            masker = butter_bandpass_filter(
                        masker,
                        stim["Mfreq1_Hz"],
                        stim["Mfreq2_Hz"],
                        sample_rate,
                        order=13,#6
            )
        else:
            print("DEBUG: NN masker")
            masker=np.random.uniform(
                low=-1.0,
                high=1.0,
                size=int(round(Mdur_s * sample_rate)),
            )
            masker = butter_bandstop_filter(
                masker,
                stim["Mfreq3_Hz"],
                stim["Mfreq4_Hz"],
                sample_rate,
                order=33,#6
            )
            masker = butter_bandpass_filter(
                masker,
                stim["Mfreq1_Hz"],
                stim["Mfreq2_Hz"],
                sample_rate,
                order=33,#6
            )
        #
        masker[0:on.size] *= on
        masker[-on.size:] *= np.flip(on)
        masker *= 32767 / np.max(np.abs(masker))
        masker *= 10**(-matt/20)#attenuate
        if stim["Monset_ms"] > 0.0:
            beforeM = np.zeros((int(round(Monset_s * sample_rate)),))
            masker = np.hstack((beforeM, masker))
        if Mend_ms < maxdur_ms:
            afterM = np.zeros((int(round((maxdur_s - Mend_s) * sample_rate)),))#changed from round
            masker = np.hstack((masker, afterM))
    #2. generate silent-target
    #silenttarget = np.zeros((int(round(maxdur_s * sample_rate)),))#maxdur_s of silence, here was round
    silenttarget = np.zeros((masker.size,))#maxdur_s of silence, here was round
    #3. generate target
    t = np.linspace(0, Tdur_s, int(round(Tdur_s * sample_rate)), False)
    target = np.sin(stim["Tfreq_Hz"] * t * 2 * np.pi)
    target[0:on.size] *= on
    target[-on.size:] *= np.flip(on)
    target *= 32767 / np.max(np.abs(target))
    target *= 10**(-tatt/20)#attenuate
    if stim["Tonset_ms"] > 0.0:
        beforeT = np.zeros((int(round(Tonset_s * sample_rate)),))
        target = np.hstack((beforeT, target))
    if Tend_ms < maxdur_ms:
        afterT = np.zeros((int(round((maxdur_s - Tend_s) * sample_rate)),))
        target = np.hstack((target, afterT))
    if target.size < masker.size:
        target = np.hstack((target, 0))
    if target.size > masker.size:
        target = target[1:]
    #4. add masker+target & masker+silent-target
    maskeronly = masker + silenttarget
    maskertarget = masker + target
    maskeronly = maskeronly.astype(np.int16)
    maskertarget = maskertarget.astype(np.int16)
#    #DEBUG
#    import matplotlib.pyplot as plt
#    plt.plot(maskertarget,'k-')
#    plt.plot(maskeronly,'r-')
#    print(str(maskertarget.size))
#    print(str(maskeronly.size))
#    plt.show()
    #5. generate 3 audio snippets in the correct order
    order = np.random.permutation(3)+1.0
    correctanswer = int(np.where(order==1.0)[0]+1)
    if force1:
        correctanswer = 1
    if correctanswer == 1:
        A = {
                "aud1": maskertarget, 
                "aud2": maskeronly,
                "aud3": maskeronly,
                "correctanswer": correctanswer,
            }
    elif correctanswer == 2:
        A = {
                "aud1": maskeronly, 
                "aud2": maskertarget,
                "aud3": maskeronly,
                "correctanswer": correctanswer,
            }
    else:
        A = {
                "aud1": maskeronly, 
                "aud2": maskeronly,
                "aud3": maskertarget,
                "correctanswer": correctanswer,
            }
    return(A)

def provideaudio_old(condnr, att):
        """
        This should generate the correct audio stimuli and can be very complex.
        It should get its input data from a configuration object or file written
        by a different gui?
        """
        #order = np.random.permutation(3)+1.0
        #self.correctanswer = int(np.where(order==1.0)[0]+1)
        sample_rate = 44100
        rampdur = 0.002
        on = np.sin(np.linspace(0,0.5*np.pi,int(round(rampdur*sample_rate))))
        #generate masker noise
        TN = 0.5#duration in s
        rmslevel = 1.0/1.414
        noise = np.random.normal(0,rmslevel,int(round(TN * sample_rate)))
        noise[noise>1]=1
        noise[noise<-1]=-1
        lowcut = 200.0
        highcut = 20000.0
        noise = butter_bandpass_filter(
            noise, lowcut, highcut, sample_rate, order=6,
        )
        noise[0:on.size] *= on
        noise[-on.size:] *= np.flip(on)
        noise *= 32767 / np.max(np.abs(noise))
        #
        #generate silence
        TS = 0.005#duration in s
        gap = np.zeros((int(round(TS * sample_rate)),))
        #
        A_freq = 440
        #Csh_freq = A_freq * 2 ** (4 / 12)
        #E_freq = A_freq * 2 ** (7 / 12)
        T = 0.33
        t = np.linspace(0, T, int(round(T * sample_rate)), False)
        # generate sine wave notes
        if condnr == 1:
            target = np.sin(A_freq * t * 2 * np.pi)
            target[0:on.size] *= on
            target[-on.size:] *= np.flip(on)
            target *= 32767 / np.max(np.abs(target))#normalize to 16bit range
            target *= 10**(-att/20)#attenuate
            #target = np.sin(E_freq * t * 2 * np.pi)
            #target = np.sin(Csh_freq * t * 2 * np.pi)
        else:
            target = np.zeros((t.size,))
        audio = np.hstack((noise, gap, target))
        # convert to 16-bit data
        audio = audio.astype(np.int16)
        return(audio)
#--------------------- END OF-AUDIO HELPER FUNCTIONS---------------------------


def main(): 
    root = tk.Tk()
    app = Preparewindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
