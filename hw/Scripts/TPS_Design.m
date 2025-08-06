% TPS43060 Design


V_in = [20 28];
V_start = 22;
V_stop = 20;
I_out_max = 3;
V_out = 49;
K_ind = 0.3; % Value to steer output ripple
f_sw = 750e3;
V_csmax = 68e-3;
V_csmax_max = 82e-3;
V_en_dis = 1.14;
V_en_on = 1.21;
I_en_pup = 1.8e-6;
I_en_hys = 3.2e-6;

D = (V_out-V_in)/V_out
D_max = max(D);
D_min = min(D);
f_sw_on = D_min/100e-9
f_sw_off = (1-D_max)/250e-9

f_sw_max = max(f_sw_off,f_sw_on)

I_inmax = I_out_max/(1-D_max)


L_min = V_out/(I_inmax*K_ind)*1/(4*f_sw);

L = e_series(L_min,'e12', 'up')

I_l_rms = sqrt((I_out_max/(1-D_max))^2+((V_in(1)*D_max)/(sqrt(12)*L*f_sw))^2)
I_l_peak = I_out_max/(1-D_max)+(V_in(1)*D_max)/(2*L*f_sw) 


R_csmin = V_csmax/(1.2*I_l_peak)
R_cs = 6.8e-3;
P_rcs = V_csmax_max ^2/R_cs
R_RT = e_series(57500/(f_sw/1000) *1000)

R_uvlo_h=e_series((V_start*(V_en_dis/V_en_on)-V_stop)/(I_en_pup*(1-V_en_dis/V_en_on)+I_en_hys))
R_uvlo_l= e_series(R_uvlo_h * V_en_dis/(V_stop-V_en_dis+R_uvlo_h*(I_en_hys+I_en_hys)))


Vinmin = min(V_in);
Rsense = 0.005;
Cout = 20e-6;
ESR = 1e-3;
L = 8.2e-6;
Rsh = 470e3;
Rsl = 12e3;
Gea= 1.1e-3;

Adc = 3/40 * Vinmin/(2*Rsense*I_out_max)
fpmod = 1/(2*pi*V_out/I_out_max * Cout);
fzmod = 1/(2*pi*ESR*Cout);

frhpz = V_out/(2*pi*L*I_out_max)*(Vinmin/V_out)^2;

fco = min(frhpz/4,f_sw/5);
R76 = 40/3*2*pi*Cout * Rsense*V_out * fco * (Rsh+Rsl)/(Rsl*Vinmin*Gea)
C70 = 40/3*1/(2*pi*fco/10*R76)
C69 = max(Cout*ESR/R76, 1/(20*pi * fco*R76))