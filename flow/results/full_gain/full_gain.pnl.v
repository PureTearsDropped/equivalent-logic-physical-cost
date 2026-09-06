module full_gain (VPWR,
    VGND,
    a,
    b,
    p);
 inout VPWR;
 inout VGND;
 input [3:0] a;
 input [3:0] b;
 output [7:0] p;

 wire n10;
 wire n100;
 wire n101;
 wire n102;
 wire n103;
 wire n104;
 wire n106;
 wire n107;
 wire n108;
 wire n109;
 wire n11;
 wire n110;
 wire n111;
 wire n112;
 wire n113;
 wire n115;
 wire n116;
 wire n117;
 wire n118;
 wire n119;
 wire n12;
 wire n120;
 wire n121;
 wire n122;
 wire n125;
 wire n126;
 wire n127;
 wire n128;
 wire n129;
 wire n13;
 wire n14;
 wire n15;
 wire n16;
 wire n17;
 wire n18;
 wire n19;
 wire n20;
 wire n21;
 wire n22;
 wire n23;
 wire n24;
 wire n25;
 wire n26;
 wire n27;
 wire n28;
 wire n29;
 wire n30;
 wire n31;
 wire n32;
 wire n33;
 wire n34;
 wire n35;
 wire n36;
 wire n37;
 wire n38;
 wire n39;
 wire n40;
 wire n41;
 wire n42;
 wire n44;
 wire n45;
 wire n46;
 wire n47;
 wire n48;
 wire n49;
 wire n50;
 wire n51;
 wire n52;
 wire n53;
 wire n54;
 wire n55;
 wire n56;
 wire n57;
 wire n58;
 wire n59;
 wire n60;
 wire n61;
 wire n62;
 wire n63;
 wire n64;
 wire n65;
 wire n66;
 wire n67;
 wire n68;
 wire n69;
 wire n70;
 wire n72;
 wire n73;
 wire n74;
 wire n75;
 wire n76;
 wire n77;
 wire n78;
 wire n79;
 wire n8;
 wire n80;
 wire n81;
 wire n82;
 wire n83;
 wire n84;
 wire n85;
 wire n86;
 wire n87;
 wire n88;
 wire n89;
 wire n90;
 wire n91;
 wire n92;
 wire n93;
 wire n94;
 wire n95;
 wire n97;
 wire n98;
 wire n99;

 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_13 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Left_23 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Right_10 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Left_24 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Right_11 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Left_25 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Right_12 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_14 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_15 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_16 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_17 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_18 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_19 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_20 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_21 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Left_22 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Right_9 (.VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_26 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_27 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_10_37 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_38 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_39 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_40 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_1_28 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_29 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_3_30 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_31 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_5_32 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_33 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_7_34 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_35 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_9_36 (.VGND(VGND),
    .VPWR(VPWR));
 sky130_fd_sc_hd__nand2_1 g0 (.A(a[0]),
    .B(b[0]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n8));
 sky130_fd_sc_hd__inv_1 g1 (.A(n8),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[0]));
 sky130_fd_sc_hd__nand2_2 g10 (.A(a[1]),
    .B(b[1]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n18));
 sky130_fd_sc_hd__nand2_1 g100 (.A(n91),
    .B(n107),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n108));
 sky130_fd_sc_hd__nand2_1 g101 (.A(n37),
    .B(n107),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n109));
 sky130_fd_sc_hd__nand2_1 g102 (.A(n108),
    .B(n109),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n110));
 sky130_fd_sc_hd__nand2_1 g103 (.A(n110),
    .B(n106),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n111));
 sky130_fd_sc_hd__nand2_1 g104 (.A(n110),
    .B(n111),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n112));
 sky130_fd_sc_hd__nand2_1 g105 (.A(n106),
    .B(n111),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n113));
 sky130_fd_sc_hd__nand2_1 g106 (.A(n112),
    .B(n113),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[5]));
 sky130_fd_sc_hd__nand2_1 g107 (.A(n107),
    .B(n125),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n115));
 sky130_fd_sc_hd__nand2_1 g108 (.A(n92),
    .B(n39),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n116));
 sky130_fd_sc_hd__nand2_1 g109 (.A(n92),
    .B(n116),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n117));
 sky130_fd_sc_hd__inv_2 g11 (.A(n18),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n19));
 sky130_fd_sc_hd__nand2_1 g110 (.A(n39),
    .B(n116),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n118));
 sky130_fd_sc_hd__nand2_1 g111 (.A(n117),
    .B(n118),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n119));
 sky130_fd_sc_hd__nand2_2 g112 (.A(n119),
    .B(n115),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n120));
 sky130_fd_sc_hd__nand2_1 g113 (.A(n119),
    .B(n120),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n121));
 sky130_fd_sc_hd__nand2_1 g114 (.A(n115),
    .B(n120),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n122));
 sky130_fd_sc_hd__nand2_2 g115 (.A(n121),
    .B(n122),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[6]));
 sky130_fd_sc_hd__nand2_1 g116 (.A(n116),
    .B(n120),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[7]));
 sky130_fd_sc_hd__nand2_1 g117 (.A(n110),
    .B(n106),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n125));
 sky130_fd_sc_hd__nand2_1 g118 (.A(n127),
    .B(n44),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n126));
 sky130_fd_sc_hd__nand2_1 g119 (.A(n46),
    .B(n47),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n127));
 sky130_fd_sc_hd__nand2_1 g12 (.A(a[1]),
    .B(b[2]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n20));
 sky130_fd_sc_hd__nand2_1 g120 (.A(n66),
    .B(n29),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n128));
 sky130_fd_sc_hd__nand2_1 g121 (.A(n54),
    .B(n58),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n129));
 sky130_fd_sc_hd__inv_1 g13 (.A(n20),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n21));
 sky130_fd_sc_hd__nand2_1 g14 (.A(a[1]),
    .B(b[3]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n22));
 sky130_fd_sc_hd__inv_1 g15 (.A(n22),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n23));
 sky130_fd_sc_hd__nand2_1 g16 (.A(a[2]),
    .B(b[0]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n24));
 sky130_fd_sc_hd__inv_1 g17 (.A(n24),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n25));
 sky130_fd_sc_hd__nand2_1 g18 (.A(a[2]),
    .B(b[1]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n26));
 sky130_fd_sc_hd__inv_1 g19 (.A(n26),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n27));
 sky130_fd_sc_hd__nand2_1 g2 (.A(a[0]),
    .B(b[1]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n10));
 sky130_fd_sc_hd__nand2_1 g20 (.A(a[2]),
    .B(b[2]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n28));
 sky130_fd_sc_hd__inv_1 g21 (.A(n28),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n29));
 sky130_fd_sc_hd__nand2_1 g22 (.A(a[2]),
    .B(b[3]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n30));
 sky130_fd_sc_hd__inv_1 g23 (.A(n30),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n31));
 sky130_fd_sc_hd__nand2_1 g24 (.A(a[3]),
    .B(b[0]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n32));
 sky130_fd_sc_hd__inv_1 g25 (.A(n32),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n33));
 sky130_fd_sc_hd__nand2_1 g26 (.A(a[3]),
    .B(b[1]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n34));
 sky130_fd_sc_hd__inv_1 g27 (.A(n34),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n35));
 sky130_fd_sc_hd__nand2_1 g28 (.A(a[3]),
    .B(b[2]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n36));
 sky130_fd_sc_hd__inv_1 g29 (.A(n36),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n37));
 sky130_fd_sc_hd__inv_1 g3 (.A(n10),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n11));
 sky130_fd_sc_hd__nand2_1 g30 (.A(a[3]),
    .B(b[3]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n38));
 sky130_fd_sc_hd__inv_1 g31 (.A(n38),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n39));
 sky130_fd_sc_hd__nand2_1 g32 (.A(n17),
    .B(n11),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n40));
 sky130_fd_sc_hd__nand2_1 g33 (.A(n17),
    .B(n40),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n41));
 sky130_fd_sc_hd__nand2_1 g34 (.A(n11),
    .B(n40),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n42));
 sky130_fd_sc_hd__nand2_1 g35 (.A(n41),
    .B(n42),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[1]));
 sky130_fd_sc_hd__inv_1 g36 (.A(n40),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n44));
 sky130_fd_sc_hd__nand2_2 g37 (.A(n19),
    .B(n13),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n45));
 sky130_fd_sc_hd__nand2_1 g38 (.A(n19),
    .B(n45),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n46));
 sky130_fd_sc_hd__nand2_1 g39 (.A(n13),
    .B(n45),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n47));
 sky130_fd_sc_hd__nand2_4 g4 (.A(a[0]),
    .B(b[2]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n12));
 sky130_fd_sc_hd__nand2_1 g40 (.A(n46),
    .B(n47),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n48));
 sky130_fd_sc_hd__nand2_1 g41 (.A(n48),
    .B(n44),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n49));
 sky130_fd_sc_hd__nand2_1 g42 (.A(n48),
    .B(n49),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n50));
 sky130_fd_sc_hd__nand2_1 g43 (.A(n44),
    .B(n49),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n51));
 sky130_fd_sc_hd__nand2_1 g44 (.A(n50),
    .B(n51),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n52));
 sky130_fd_sc_hd__nand2_1 g45 (.A(n45),
    .B(n126),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n53));
 sky130_fd_sc_hd__nand2_1 g46 (.A(n21),
    .B(n15),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n54));
 sky130_fd_sc_hd__nand2_1 g47 (.A(n21),
    .B(n54),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n55));
 sky130_fd_sc_hd__nand2_1 g48 (.A(n15),
    .B(n54),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n56));
 sky130_fd_sc_hd__nand2_1 g49 (.A(n55),
    .B(n56),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n57));
 sky130_fd_sc_hd__inv_2 g5 (.A(n12),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n13));
 sky130_fd_sc_hd__nand2_1 g50 (.A(n57),
    .B(n53),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n58));
 sky130_fd_sc_hd__nand2_1 g51 (.A(n57),
    .B(n58),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n59));
 sky130_fd_sc_hd__nand2_1 g52 (.A(n53),
    .B(n58),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n60));
 sky130_fd_sc_hd__nand2_1 g53 (.A(n59),
    .B(n60),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n61));
 sky130_fd_sc_hd__nand2_1 g54 (.A(n54),
    .B(n58),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n62));
 sky130_fd_sc_hd__nand2_1 g55 (.A(n23),
    .B(n129),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n63));
 sky130_fd_sc_hd__nand2_1 g56 (.A(n23),
    .B(n63),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n64));
 sky130_fd_sc_hd__nand2_1 g57 (.A(n62),
    .B(n63),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n65));
 sky130_fd_sc_hd__nand2_1 g58 (.A(n64),
    .B(n65),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n66));
 sky130_fd_sc_hd__inv_1 g59 (.A(n63),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n67));
 sky130_fd_sc_hd__nand2_1 g6 (.A(a[0]),
    .B(b[3]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n14));
 sky130_fd_sc_hd__nand2_1 g60 (.A(n52),
    .B(n25),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n68));
 sky130_fd_sc_hd__nand2_1 g61 (.A(n52),
    .B(n68),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n69));
 sky130_fd_sc_hd__nand2_1 g62 (.A(n25),
    .B(n68),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n70));
 sky130_fd_sc_hd__nand2_1 g63 (.A(n69),
    .B(n70),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[2]));
 sky130_fd_sc_hd__inv_1 g64 (.A(n68),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n72));
 sky130_fd_sc_hd__xor3_2 g65 (.A(n61),
    .B(n27),
    .C(n72),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .X(n73));
 sky130_fd_sc_hd__maj3_2 g66 (.A(n61),
    .B(n27),
    .C(n72),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .X(n74));
 sky130_fd_sc_hd__nand2_1 g67 (.A(n66),
    .B(n29),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n75));
 sky130_fd_sc_hd__nand2_1 g68 (.A(n66),
    .B(n128),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n76));
 sky130_fd_sc_hd__nand2_1 g69 (.A(n29),
    .B(n75),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n77));
 sky130_fd_sc_hd__inv_1 g7 (.A(n14),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n15));
 sky130_fd_sc_hd__nand2_1 g70 (.A(n76),
    .B(n77),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n78));
 sky130_fd_sc_hd__nand2_2 g71 (.A(n78),
    .B(n74),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n79));
 sky130_fd_sc_hd__nand2_1 g72 (.A(n78),
    .B(n79),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n80));
 sky130_fd_sc_hd__nand2_1 g73 (.A(n74),
    .B(n79),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n81));
 sky130_fd_sc_hd__nand2_1 g74 (.A(n80),
    .B(n81),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n82));
 sky130_fd_sc_hd__nand2_1 g75 (.A(n75),
    .B(n79),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n83));
 sky130_fd_sc_hd__nand2_1 g76 (.A(n67),
    .B(n31),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n84));
 sky130_fd_sc_hd__nand2_1 g77 (.A(n67),
    .B(n84),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n85));
 sky130_fd_sc_hd__nand2_1 g78 (.A(n31),
    .B(n84),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n86));
 sky130_fd_sc_hd__nand2_1 g79 (.A(n85),
    .B(n86),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n87));
 sky130_fd_sc_hd__nand2_1 g8 (.A(a[1]),
    .B(b[0]),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n16));
 sky130_fd_sc_hd__nand2_1 g80 (.A(n87),
    .B(n83),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n88));
 sky130_fd_sc_hd__nand2_1 g81 (.A(n87),
    .B(n88),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n89));
 sky130_fd_sc_hd__nand2_1 g82 (.A(n83),
    .B(n88),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n90));
 sky130_fd_sc_hd__nand2_1 g83 (.A(n89),
    .B(n90),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n91));
 sky130_fd_sc_hd__nand2_1 g84 (.A(n84),
    .B(n88),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n92));
 sky130_fd_sc_hd__nand2_1 g85 (.A(n73),
    .B(n33),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n93));
 sky130_fd_sc_hd__nand2_1 g86 (.A(n73),
    .B(n93),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n94));
 sky130_fd_sc_hd__nand2_1 g87 (.A(n33),
    .B(n93),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n95));
 sky130_fd_sc_hd__nand2_1 g88 (.A(n94),
    .B(n95),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[3]));
 sky130_fd_sc_hd__inv_1 g89 (.A(n93),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n97));
 sky130_fd_sc_hd__inv_1 g9 (.A(n16),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n17));
 sky130_fd_sc_hd__nand2_1 g90 (.A(n82),
    .B(n35),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n98));
 sky130_fd_sc_hd__nand2_1 g91 (.A(n82),
    .B(n98),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n99));
 sky130_fd_sc_hd__nand2_1 g92 (.A(n35),
    .B(n98),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n100));
 sky130_fd_sc_hd__nand2_1 g93 (.A(n99),
    .B(n100),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n101));
 sky130_fd_sc_hd__nand2_1 g94 (.A(n101),
    .B(n97),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n102));
 sky130_fd_sc_hd__nand2_1 g95 (.A(n101),
    .B(n102),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n103));
 sky130_fd_sc_hd__nand2_1 g96 (.A(n97),
    .B(n102),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n104));
 sky130_fd_sc_hd__nand2_1 g97 (.A(n103),
    .B(n104),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(p[4]));
 sky130_fd_sc_hd__nand2_1 g98 (.A(n98),
    .B(n102),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n106));
 sky130_fd_sc_hd__nand2_1 g99 (.A(n91),
    .B(n37),
    .VGND(VGND),
    .VNB(VGND),
    .VPB(VPWR),
    .VPWR(VPWR),
    .Y(n107));
endmodule
