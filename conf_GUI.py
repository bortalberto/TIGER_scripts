from Tkinter import *
import numpy as np
from lib import GEM_COM_classes as COM_class
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array


OS = sys.platform
if OS == 'win32':
	sep = '\\'
elif OS == 'linux2':
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	sys.exit()


class menu():
    def __init__(self):
        self.GEM_to_config = np.zeros((20))
        self.configuring_gemroc=0
        #main window
        self.main_window=Tk()
        self.main_window.title("GEMROC configurer")
        self.handler_list=[]
        self.GEMROC_reading_dict={}
        self.showing_GEMROC = StringVar(self.main_window)
        self.entry_text=StringVar(self.main_window)

        self.showing_TIGER =StringVar(self.main_window)
        self.showing_CHANNEL= 0
        self.configure_MODE=StringVar(self.main_window)
        fields_options=["DAQ configuration", "LV configuration", "Global Tiger configuration", "Channel Tiger configuration"]
        Label(self.main_window,text='Configuration',font=("Courier", 25)).pack()

        self.first_row_frame=Frame(self.main_window)
        self.first_row_frame.pack()
        self.select_MODE = OptionMenu(self.first_row_frame, self.configure_MODE,*fields_options)
        self.select_MODE.grid(row=0, column=0, sticky=NW, pady=4)

        self.second_row_frame=Frame(self.main_window)
        self.second_row_frame.pack()


        self.configure_MODE.trace('w',self.update_menu)

        self.third_row_frame = Frame(self.main_window)


        ##Select window
        self.select_window = Toplevel(self.main_window)
        self.icon_on = PhotoImage(file="."+sep+'icons'+sep+'on.gif')
        self.icon_off = PhotoImage(file="."+sep+'icons'+sep+'off.gif')
        self.icon_bad = PhotoImage(file="."+sep+'icons'+sep+'bad.gif')
        Label(self.select_window,text='GEMROC to configure',font=("Courier", 25)).pack()
        self.grid_frame=Frame(self.select_window)
        self.grid_frame.pack()
        Button(self.grid_frame, text='ROC 00', command=lambda: self.toggle(0)).grid(row=0, column=0, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 01', command=lambda: self.toggle(1)).grid(row=0, column=2, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 02', command=lambda: self.toggle(2)).grid(row=0, column=4, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 03', command=lambda: self.toggle(3)).grid(row=0, column=6, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 04', command=lambda: self.toggle(4)).grid(row=0, column=8, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 05', command=lambda: self.toggle(5)).grid(row=0, column=10, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 06', command=lambda: self.toggle(6)).grid(row=0, column=12, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 07', command=lambda: self.toggle(7)).grid(row=0, column=14, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 08', command=lambda: self.toggle(8)).grid(row=0, column=16, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 09', command=lambda: self.toggle(9)).grid(row=0, column=18, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 10', command=lambda: self.toggle(10)).grid(row=1, column=0, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 11', command=lambda: self.toggle(11)).grid(row=1, column=2, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 12', command=lambda: self.toggle(12)).grid(row=1, column=4, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 13', command=lambda: self.toggle(13)).grid(row=1, column=6, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 14', command=lambda: self.toggle(14)).grid(row=1, column=8, sticky=W, pady=4)
        Button(self.grid_frame, text='ROC 15', command=lambda: self.toggle(15)).grid(row=1, column=10, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 16', command=lambda: self.toggle(16)).grid(row=1, column=12, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 17', command=lambda: self.toggle(17)).grid(row=1, column=14, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 18', command=lambda: self.toggle(18)).grid(row=1, column=16, sticky=NW, pady=4)
        Button(self.grid_frame, text='ROC 19', command=lambda: self.toggle(19)).grid(row=1, column=18, sticky=NW, pady=4)
        self.error_frame=Frame(self.select_window)
        self.error_frame.pack()
        Label(self.error_frame,text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        self.Launch_error_check=Label(self.error_frame, text='-', background='white')
        self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)


        self.LED=[]
        for i in range (0,len(self.GEM_to_config)):
            if i<10:
                riga=0
            else:
                riga=1

            colonna=((i)%10)*2+1
            self.LED.append( Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)


    def runna(self):
        mainloop()
        # while True:
        #     self.main_window.update_idletasks()
        #     self.main_window.update()
    def toggle(self,i):
        if self.GEM_to_config[i]==0:
            self.GEM_to_config[i]=1
        else:
            self.GEM_to_config[i]=0
        self.convert0(i)

    def convert0(self,i):
        if self.GEM_to_config[i]==1:
            try:
                self.handler_list.append(GEMROC_HANDLER(i))
                self.LED[i]["image"] = self.icon_on
            except  Exception as error:
                self.Launch_error_check['text'] = "GEMROC {}: {}".format(i,error)
                self.LED[i]["image"]=self.icon_bad
            else:
                self.Launch_error_check['text'] = "Communication with GEMROC {} enstablished".format(i)


        else:
            self.LED[i]["image"]=self.icon_off
            for j in range (0, len(self.handler_list)):
                if self.handler_list[j].GEMROC_ID==i:
                    self.handler_list[j].__del__()
                    del self.handler_list[j]
                    self.Launch_error_check['text'] = "Communication with GEMROC {} closed".format(i)
                    break
        self.update_menu(1,2,3)

    def update_menu(self, a,b ,c):
        self.second_row_frame.destroy()
        self.second_row_frame = Frame(self.main_window)
        self.second_row_frame.pack()
        self.GEMROC_reading_dict = {}
        for i in range (0,len (self.handler_list)):
            ID=self.handler_list[i].GEMROC_ID
            self.GEMROC_reading_dict["GEMROC {}".format(ID)]=self.handler_list[i]
        Label(self.second_row_frame,text='GEMROC   ').grid(row=0, column=0, sticky=NW, pady=4)
        print self.GEMROC_reading_dict.keys()
        self.select_GEMROC = OptionMenu(self.second_row_frame, self.showing_GEMROC,*self.GEMROC_reading_dict.keys() )
        self.select_GEMROC.grid(row=1, column=0, sticky=NW, pady=4)
        fields_options=["DAQ configuration", "LV configuration", "Global Tiger configuration", "Channel Tiger configuration"]

        if self.configure_MODE.get() == "DAQ configuration":
            self.Go = Button(self.second_row_frame, text='Go', command=self.DAQ_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "LV configuration":
            self.Go = Button(self.second_row_frame, text='Go', command=self.update_menu)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "Global Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=NW, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=NW, pady=4)
            self.Go=Button(self.second_row_frame, text='Go', command=self.update_menu)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get()=="Channel Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=W, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=W, pady=4)
            Label(self.second_row_frame, text='Channel   ').grid(row=0, column=2, sticky=W, pady=4)
            self.Channel_IN=Entry(self.second_row_frame, width=4,textvariable = self.entry_text)
            self.entry_text.trace("w", lambda *args: character_limit(self.entry_text))
            self.Channel_IN.grid(row=1, column=2, sticky=W, pady=4)
            self.Go = Button(self.second_row_frame, text='Go', command=self.update_menu)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)

    def DAQ_configurator(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.main_window)
        self.third_row_frame.pack()
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=0, column=0, sticky=W, pady=2)
        Button(single_use_frame, text='Read configuration', command=self.read_DAQ_CR).grid(row=0, column=1, sticky=W, pady=2)

        self.field_array=[]
        self.input_array=[]
        with open ("lib"+sep+"keys"+sep+"DAQ_cr_keys", 'r') as f:
            i=0

            for line in f.readlines():
                Label(single_use_frame,text=line).grid(row=i+1, column=0, sticky=W, pady=0)
                self.field_array.append(Label(single_use_frame,text='-'))
                self.field_array[i].grid(row=i+1, column=1, sticky=W, pady=0)
                # self.input_array.append(Entry(single_use_frame,))
                # self.input_array[i].grid(row=i, column=2, sticky=W, pady=2)
                i+=1
        another_frame=Frame(self.third_row_frame)
        another_frame.grid(row=0, column=1, sticky=W, pady=2)
        Label(another_frame,text="Change configuration",font=("Courier", 25)).grid(row=0, column=0,columnspan=8,sticky=S, pady=5)
        # modebut=Button(another_frame, text="Trigger matched",command= lambda : self.switch_mode(modebut))
        # modebut.grid(row=1, column=1, sticky=W, pady=2)

        Label(another_frame,text="TCAM_Enable_pattern").grid(row=2, column=0,sticky=S, pady=0)
        Label(another_frame,text="Periodic_FEB_TP_Enable_pattern").grid(row=3, column=0,sticky=S, pady=0)
        Label(another_frame,text="TP_repeat_burst").grid(row=4, column=0,sticky=S, pady=0)
        Label(another_frame,text="TP_Num_in_burst").grid(row=5, column=0,sticky=S, pady=0)
        Label(another_frame,text="TL_nTM_ACQ_choice").grid(row=6, column=0,sticky=S, pady=0)
        Label(another_frame,text="Periodic_L1_Enable_pattern").grid(row=7, column=0,sticky=S, pady=0)
        Label(another_frame,text="Enab_Auto_L1_from_TP_bit_param").grid(row=8, column=0,sticky=S, pady=0)
        Label(another_frame,text="Enable_DAQPause_Until_First_Trigger").grid(row=9, column=0,sticky=S, pady=0)
        # Label(another_frame,text="DAQPause_Set").grid(row=10, column=0,sticky=S, pady=0)
        #Label(another_frame,text="Tpulse_gen_w_ext_trigger_enable").grid(row=11, column=0,sticky=S, pady=0)
        Label(another_frame,text="EXT_nINT_B3clk").grid(row=12, column=0,sticky=S, pady=0)


        self.IN1=Entry(another_frame)
        self.IN1.grid(row=2, column=1,sticky=S, pady=0)
        self.IN2=Entry(another_frame)
        self.IN2.grid(row=3, column=1,sticky=S, pady=0)
        self.IN3=Entry(another_frame)
        self.IN3.grid(row=4, column=1,sticky=S, pady=0)
        self.IN4=Entry(another_frame)
        self.IN4.grid(row=5, column=1,sticky=S, pady=0)
        self.IN5=Entry(another_frame)
        self.IN5.grid(row=6, column=1,sticky=S, pady=0)
        self.IN6=Entry(another_frame)
        self.IN6.grid(row=7, column=1,sticky=S, pady=0)
        self.IN7 = Entry(another_frame)
        self.IN7.grid(row=8, column=1, sticky=S, pady=0)
        self.IN8 = Entry(another_frame)
        self.IN8.grid(row=9, column=1, sticky=S, pady=0)
        # self.IN9 = Entry(another_frame)
        # self.IN9.grid(row=10, column=1, sticky=S, pady=0)
        # self.IN10 = Entry(another_frame)
        # self.IN10.grid(row=11, column=1, sticky=S, pady=0)
        self.IN11 = Entry(another_frame)
        self.IN11.grid(row=12, column=1, sticky=S, pady=0)

        Button(another_frame, text='Set', command= self.load_DAQ_CR).grid(row=15, column=15, sticky=W, pady=2)
        Button(another_frame, text='Set on all active GEMROCs', command= self.load_DAQ_CR).grid(row=15, column=16, sticky=W, pady=2)


    def load_DAQ_CR(self):
        TCAM_Enable_pattern = int(self.IN1.get()) & 0xFF
        Periodic_FEB_TP_Enable_pattern = int(self.IN2.get()) & 0xFF
        TP_repeat_burst = int(self.IN3.get()) & 0x1
        TP_Num_in_burst = int(self.IN4.get()) & 0x1FF
        TL_nTM_ACQ_choice = int(self.IN5.get()) & 0x1
        Periodic_L1_Enable_pattern = int(self.IN6.get()) & 0x1
        Enab_Auto_L1_from_TP_bit_param = int(self.IN7.get()) & 0x1


        DI_Ext_nInt_Clk_option = int(self.IN11.get()) & 0x1
        PauseMode_Enable_Option = int(self.IN8.get()) & 0x1

        #DI_Enab_Auto_L1_from_TP_bit = int(input_array[8], 0) & 0x1  # ACR 2018-11-02 added parameter
        self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.DAQ_set(TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice, Periodic_L1_Enable_pattern, Enab_Auto_L1_from_TP_bit_param)

        print "ok"
    def switch_mode(self,modebut):
        if modebut['text']=="Trigger matched":
            modebut['text'] = "Trigger less"
        elif modebut['text']=="Trigger less":
            modebut['text'] = "Trigger matched"
    def read_DAQ_CR(self):
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Read_GEMROC_DAQ_CfgReg()
        #self.GEMROC_reading_dict[self.showing_GEMROC.get()].GEM_COM.display_log_GEMROC_DAQ_CfgReg_readback(command_reply, 1, 1)
        L_array = array.array('I')
        L_array.fromstring(command_reply)
        L_array.byteswap()
        self.field_array[0]['text']=((L_array[0] >> 16) & 0X1f)
        self.field_array[1]['text'] = ((L_array[0] >> 8) & 0xFF)
        self.field_array[2]['text'] = ((L_array[4] >> 26) & 0xF)
        self.field_array[3]['text'] = ((L_array[1] >> 20) & 0x3FF)
        self.field_array[4]['text'] = ((L_array[1] >> 16) & 0xF)
        #self.field_array[5]['text'] = ((L_array[1] >> 0) & 0xFFFF)
        self.field_array[5]['text'] = ((L_array[2] >> 20) & 0x3FF)
        #self.field_array[7]['text'] = ((L_array[2] >> 16) & 0xF)
        #self.field_array[8]['text'] = ((L_array[3] >> 12) & 0xF)  # acr 2018-11-02
        self.field_array[6]['text'] = ((L_array[3] >> 15) & 0x1)  # acr 2018-11-02
        self.field_array[7]['text'] = ((L_array[3] >> 14) & 0x1)  # acr 2018-11-02
        self.field_array[8]['text'] = ((L_array[3] >> 13) & 0x1)  # acr 2018-11-02
        self.field_array[9]['text'] = ((L_array[3] >> 12) & 0x1) # acr 2018-11-02
        #self.field_array[13]['text'] = ((L_array[2] >> 0) & 0xFFFF)
        self.field_array[10]['text'] = ((L_array[3] >> 20) & 0x3FF)
        self.field_array[11]['text'] =((L_array[3] >> 16) & 0xF)
        self.field_array[12]['text'] = ((L_array[3] >> 11) & 0x1)
        self.field_array[13]['text'] =((L_array[3] >> 10) & 0x1)
        self.field_array[14]['text'] =((L_array[3] >> 9) & 0x1)
        self.field_array[15]['text'] =((L_array[3] >> 8) & 0x1)
        self.field_array[16]['text'] = ((L_array[3] >> 0) & 0xFF)
        self.field_array[17]['text'] = ((L_array[4] >> 16) & 0x3FF)
        self.field_array[18] = ((L_array[4] >> 8) & 0x3)
        #self.field_array[23]['text'] = ((L_array[4] >> 6) & 0x1)

        self.IN1.insert(END,(L_array[3] >> 0) & 0xFF)
        self.IN2.insert(END,(L_array[3] >> 16) & 0xF)
        self.IN3.insert(END,(L_array[3] >> 9) & 0x1 )#TODO verificare!
        self.IN4.insert(END,(L_array[4] >> 16) & 0x3FF)
        self.IN5.insert(END,(L_array[3] >> 11) & 0x1)
        self.IN6.insert(END,(L_array[3] >> 16) & 0xF)
        self.IN7.insert(END, 0)

        self.IN8.insert(END,((L_array[3] >> 15) & 0x1))
        # self.IN9.insert(END,((L_array[3] >> 14) & 0x1))
        # self.IN10.insert(END,((L_array[3] >> 13) & 0x1))
        self.IN11.insert(END,((L_array[3] >> 12) & 0x1))

def character_limit(entry_text):
    try:
        if int(entry_text.get())<0:
            entry_text.set(0)
        if int(entry_text.get()) > 63:
            entry_text.set(63)
    except:
        entry_text.set("")
        "Not valid input in channel field"



class GEMROC_HANDLER:
    def __init__(self,GEMROC_ID):
        self.GEMROC_ID=GEMROC_ID
        self.GEM_COM = COM_class.communication(GEMROC_ID, 0)  # Create communication class
        default_g_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
        self.g_inst = GEM_CONF.g_reg_settings(GEMROC_ID, default_g_inst_settigs_filename)
        default_ch_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
        self.c_inst = GEM_CONF.ch_reg_settings(GEMROC_ID, default_ch_inst_settigs_filename)
    def __del__(self):
        self.GEM_COM.__del__()


Main_menu=menu()
Main_menu.runna()

