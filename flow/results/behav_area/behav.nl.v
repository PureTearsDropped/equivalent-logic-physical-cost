module behav (a,
    b,
    p);
 input [3:0] a;
 input [3:0] b;
 output [7:0] p;

 wire _000_;
 wire _001_;
 wire _002_;
 wire _003_;
 wire _004_;
 wire _005_;
 wire _006_;
 wire _007_;
 wire _008_;
 wire _009_;
 wire _010_;
 wire _011_;
 wire _012_;
 wire _013_;
 wire _014_;
 wire _015_;
 wire _016_;
 wire _017_;
 wire _018_;
 wire _019_;
 wire _020_;
 wire _021_;
 wire _022_;
 wire _023_;
 wire _024_;
 wire _025_;
 wire _026_;
 wire _027_;
 wire _028_;
 wire _029_;
 wire _030_;
 wire _031_;
 wire _032_;
 wire _033_;
 wire _034_;
 wire _035_;
 wire _036_;
 wire _037_;
 wire _038_;
 wire _039_;
 wire _040_;
 wire _041_;
 wire _042_;
 wire _043_;
 wire _044_;
 wire _045_;
 wire _046_;
 wire _047_;
 wire _048_;
 wire _049_;
 wire _050_;
 wire _051_;
 wire _052_;
 wire net1;
 wire net2;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net7;
 wire net8;
 wire net9;
 wire net10;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;

 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_13 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Left_23 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Right_10 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Left_24 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Right_11 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Left_25 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Right_12 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_14 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_15 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_16 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_17 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_18 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_19 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_20 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_21 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Left_22 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Right_9 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_26 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_27 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_10_37 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_38 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_39 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_40 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_1_28 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_29 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_3_30 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_31 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_5_32 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_33 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_7_34 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_35 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_9_36 ();
 sky130_fd_sc_hd__and2_2 _053_ (.A(net5),
    .B(net1),
    .X(net9));
 sky130_fd_sc_hd__a22oi_2 _054_ (.A1(net1),
    .A2(net6),
    .B1(net2),
    .B2(net5),
    .Y(_000_));
 sky130_fd_sc_hd__and3_2 _055_ (.A(net6),
    .B(net2),
    .C(net9),
    .X(_001_));
 sky130_fd_sc_hd__nor2_2 _056_ (.A(_000_),
    .B(_001_),
    .Y(net10));
 sky130_fd_sc_hd__a22o_2 _057_ (.A1(net6),
    .A2(net2),
    .B1(net7),
    .B2(net1),
    .X(_002_));
 sky130_fd_sc_hd__inv_2 _058_ (.A(_002_),
    .Y(_003_));
 sky130_fd_sc_hd__and4_2 _059_ (.A(net1),
    .B(net6),
    .C(net2),
    .D(net7),
    .X(_004_));
 sky130_fd_sc_hd__and4b_2 _060_ (.A_N(_004_),
    .B(net3),
    .C(net5),
    .D(_002_),
    .X(_005_));
 sky130_fd_sc_hd__o2bb2a_2 _061_ (.A1_N(net5),
    .A2_N(net3),
    .B1(_003_),
    .B2(_004_),
    .X(_006_));
 sky130_fd_sc_hd__nor2_2 _062_ (.A(_005_),
    .B(_006_),
    .Y(_007_));
 sky130_fd_sc_hd__nand2_2 _063_ (.A(_001_),
    .B(_007_),
    .Y(_008_));
 sky130_fd_sc_hd__nand2_2 _064_ (.A(net2),
    .B(net8),
    .Y(_009_));
 sky130_fd_sc_hd__nand4_2 _065_ (.A(net1),
    .B(net2),
    .C(net8),
    .D(net7),
    .Y(_010_));
 sky130_fd_sc_hd__a22o_2 _066_ (.A1(net1),
    .A2(net8),
    .B1(net7),
    .B2(net2),
    .X(_011_));
 sky130_fd_sc_hd__nand4_2 _067_ (.A(net6),
    .B(net3),
    .C(_010_),
    .D(_011_),
    .Y(_012_));
 sky130_fd_sc_hd__a22o_2 _068_ (.A1(net6),
    .A2(net3),
    .B1(_010_),
    .B2(_011_),
    .X(_013_));
 sky130_fd_sc_hd__nand3_2 _069_ (.A(_004_),
    .B(_012_),
    .C(_013_),
    .Y(_014_));
 sky130_fd_sc_hd__a21o_2 _070_ (.A1(_012_),
    .A2(_013_),
    .B1(_004_),
    .X(_015_));
 sky130_fd_sc_hd__nand4_2 _071_ (.A(net5),
    .B(net4),
    .C(_014_),
    .D(_015_),
    .Y(_016_));
 sky130_fd_sc_hd__a22o_2 _072_ (.A1(net5),
    .A2(net4),
    .B1(_014_),
    .B2(_015_),
    .X(_017_));
 sky130_fd_sc_hd__and3_2 _073_ (.A(_005_),
    .B(_016_),
    .C(_017_),
    .X(_018_));
 sky130_fd_sc_hd__a21oi_2 _074_ (.A1(_016_),
    .A2(_017_),
    .B1(_005_),
    .Y(_019_));
 sky130_fd_sc_hd__nor2_2 _075_ (.A(_018_),
    .B(_019_),
    .Y(_020_));
 sky130_fd_sc_hd__xnor2_2 _076_ (.A(_008_),
    .B(_020_),
    .Y(net12));
 sky130_fd_sc_hd__nand2_2 _077_ (.A(_010_),
    .B(_012_),
    .Y(_021_));
 sky130_fd_sc_hd__nand2_2 _078_ (.A(net6),
    .B(net4),
    .Y(_022_));
 sky130_fd_sc_hd__and4_2 _079_ (.A(net2),
    .B(net8),
    .C(net7),
    .D(net3),
    .X(_023_));
 sky130_fd_sc_hd__nand2_2 _080_ (.A(net7),
    .B(net3),
    .Y(_024_));
 sky130_fd_sc_hd__a21oi_2 _081_ (.A1(_009_),
    .A2(_024_),
    .B1(_023_),
    .Y(_025_));
 sky130_fd_sc_hd__xnor2_2 _082_ (.A(_022_),
    .B(_025_),
    .Y(_026_));
 sky130_fd_sc_hd__and2_2 _083_ (.A(_021_),
    .B(_026_),
    .X(_027_));
 sky130_fd_sc_hd__xnor2_2 _084_ (.A(_021_),
    .B(_026_),
    .Y(_028_));
 sky130_fd_sc_hd__and2_2 _085_ (.A(_014_),
    .B(_016_),
    .X(_029_));
 sky130_fd_sc_hd__nor2_2 _086_ (.A(_028_),
    .B(_029_),
    .Y(_030_));
 sky130_fd_sc_hd__or2_2 _087_ (.A(_028_),
    .B(_029_),
    .X(_031_));
 sky130_fd_sc_hd__and3_2 _088_ (.A(_014_),
    .B(_016_),
    .C(_028_),
    .X(_032_));
 sky130_fd_sc_hd__nor2_2 _089_ (.A(_030_),
    .B(_032_),
    .Y(_033_));
 sky130_fd_sc_hd__o21ba_2 _090_ (.A1(_008_),
    .A2(_019_),
    .B1_N(_018_),
    .X(_034_));
 sky130_fd_sc_hd__xnor2_2 _091_ (.A(_033_),
    .B(_034_),
    .Y(net13));
 sky130_fd_sc_hd__a31o_2 _092_ (.A1(net6),
    .A2(net4),
    .A3(_025_),
    .B1(_023_),
    .X(_035_));
 sky130_fd_sc_hd__a22o_2 _093_ (.A1(net8),
    .A2(net3),
    .B1(net4),
    .B2(net7),
    .X(_036_));
 sky130_fd_sc_hd__nand4_2 _094_ (.A(net8),
    .B(net7),
    .C(net3),
    .D(net4),
    .Y(_037_));
 sky130_fd_sc_hd__nand2_2 _095_ (.A(_036_),
    .B(_037_),
    .Y(_038_));
 sky130_fd_sc_hd__and3_2 _096_ (.A(_035_),
    .B(_036_),
    .C(_037_),
    .X(_039_));
 sky130_fd_sc_hd__xnor2_2 _097_ (.A(_035_),
    .B(_038_),
    .Y(_040_));
 sky130_fd_sc_hd__nor2_2 _098_ (.A(_027_),
    .B(_040_),
    .Y(_041_));
 sky130_fd_sc_hd__and2_2 _099_ (.A(_027_),
    .B(_040_),
    .X(_042_));
 sky130_fd_sc_hd__nor2_2 _100_ (.A(_041_),
    .B(_042_),
    .Y(_043_));
 sky130_fd_sc_hd__o21a_2 _101_ (.A1(_032_),
    .A2(_034_),
    .B1(_031_),
    .X(_044_));
 sky130_fd_sc_hd__xnor2_2 _102_ (.A(_043_),
    .B(_044_),
    .Y(net14));
 sky130_fd_sc_hd__and2b_2 _103_ (.A_N(_034_),
    .B(_040_),
    .X(_045_));
 sky130_fd_sc_hd__nor2_2 _104_ (.A(_031_),
    .B(_041_),
    .Y(_046_));
 sky130_fd_sc_hd__and3_2 _105_ (.A(net8),
    .B(net4),
    .C(_024_),
    .X(_047_));
 sky130_fd_sc_hd__xor2_2 _106_ (.A(_039_),
    .B(_047_),
    .X(_048_));
 sky130_fd_sc_hd__o31a_2 _107_ (.A1(_042_),
    .A2(_045_),
    .A3(_046_),
    .B1(_048_),
    .X(_049_));
 sky130_fd_sc_hd__or4_2 _108_ (.A(_042_),
    .B(_045_),
    .C(_046_),
    .D(_048_),
    .X(_050_));
 sky130_fd_sc_hd__and2b_2 _109_ (.A_N(_049_),
    .B(_050_),
    .X(net15));
 sky130_fd_sc_hd__a21bo_2 _110_ (.A1(_039_),
    .A2(_047_),
    .B1_N(_037_),
    .X(_051_));
 sky130_fd_sc_hd__or2_2 _111_ (.A(_049_),
    .B(_051_),
    .X(net16));
 sky130_fd_sc_hd__or2_2 _112_ (.A(_001_),
    .B(_007_),
    .X(_052_));
 sky130_fd_sc_hd__and2_2 _113_ (.A(_008_),
    .B(_052_),
    .X(net11));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input1 (.A(a[0]),
    .X(net1));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input2 (.A(a[1]),
    .X(net2));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input3 (.A(a[2]),
    .X(net3));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input4 (.A(a[3]),
    .X(net4));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input5 (.A(b[0]),
    .X(net5));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input6 (.A(b[1]),
    .X(net6));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input7 (.A(b[2]),
    .X(net7));
 sky130_fd_sc_hd__clkdlybuf4s25_1 input8 (.A(b[3]),
    .X(net8));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output10 (.A(net10),
    .X(p[1]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output11 (.A(net11),
    .X(p[2]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output12 (.A(net12),
    .X(p[3]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output13 (.A(net13),
    .X(p[4]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output14 (.A(net14),
    .X(p[5]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output15 (.A(net15),
    .X(p[6]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output16 (.A(net16),
    .X(p[7]));
 sky130_fd_sc_hd__clkdlybuf4s25_1 output9 (.A(net9),
    .X(p[0]));
endmodule
