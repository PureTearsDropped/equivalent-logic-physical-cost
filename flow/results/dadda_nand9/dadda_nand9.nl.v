module dadda_nand9 (a,
    b,
    p);
 input [3:0] a;
 input [3:0] b;
 output [7:0] p;

 wire n10;
 wire n100;
 wire n101;
 wire n102;
 wire n104;
 wire n105;
 wire n106;
 wire n107;
 wire n108;
 wire n109;
 wire n11;
 wire n110;
 wire n111;
 wire n113;
 wire n114;
 wire n115;
 wire n116;
 wire n117;
 wire n118;
 wire n119;
 wire n12;
 wire n120;
 wire n122;
 wire n123;
 wire n124;
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
 wire n43;
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
 wire n71;
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
 wire n86;
 wire n87;
 wire n88;
 wire n89;
 wire n90;
 wire n91;
 wire n92;
 wire n93;
 wire n95;
 wire n96;
 wire n97;
 wire n98;
 wire n99;

 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_12 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Left_22 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Right_10 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Left_23 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Right_11 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_13 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_14 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_15 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_16 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_17 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_18 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_19 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_20 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Left_21 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Right_9 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_24 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_25 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_10_35 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_36 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_37 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_1_26 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_27 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_3_28 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_29 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_5_30 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_31 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_7_32 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_33 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_9_34 ();
 sky130_fd_sc_hd__nand2_1 g0 (.A(a[0]),
    .B(b[0]),
    .Y(n8));
 sky130_fd_sc_hd__inv_1 g1 (.A(n8),
    .Y(p[0]));
 sky130_fd_sc_hd__nand2_1 g10 (.A(a[1]),
    .B(b[1]),
    .Y(n18));
 sky130_fd_sc_hd__nand2_1 g100 (.A(n106),
    .B(n107),
    .Y(n108));
 sky130_fd_sc_hd__nand2_1 g101 (.A(n108),
    .B(n104),
    .Y(n109));
 sky130_fd_sc_hd__nand2_1 g102 (.A(n108),
    .B(n109),
    .Y(n110));
 sky130_fd_sc_hd__nand2_1 g103 (.A(n104),
    .B(n109),
    .Y(n111));
 sky130_fd_sc_hd__nand2_1 g104 (.A(n110),
    .B(n111),
    .Y(p[4]));
 sky130_fd_sc_hd__nand2_1 g105 (.A(n105),
    .B(n109),
    .Y(n113));
 sky130_fd_sc_hd__nand2_1 g106 (.A(n80),
    .B(n72),
    .Y(n114));
 sky130_fd_sc_hd__nand2_1 g107 (.A(n80),
    .B(n114),
    .Y(n115));
 sky130_fd_sc_hd__nand2_1 g108 (.A(n72),
    .B(n114),
    .Y(n116));
 sky130_fd_sc_hd__nand2_1 g109 (.A(n115),
    .B(n116),
    .Y(n117));
 sky130_fd_sc_hd__inv_1 g11 (.A(n18),
    .Y(n19));
 sky130_fd_sc_hd__nand2_1 g110 (.A(n117),
    .B(n113),
    .Y(n118));
 sky130_fd_sc_hd__nand2_1 g111 (.A(n117),
    .B(n118),
    .Y(n119));
 sky130_fd_sc_hd__nand2_1 g112 (.A(n113),
    .B(n118),
    .Y(n120));
 sky130_fd_sc_hd__nand2_1 g113 (.A(n119),
    .B(n120),
    .Y(p[5]));
 sky130_fd_sc_hd__nand2_1 g114 (.A(n114),
    .B(n118),
    .Y(n122));
 sky130_fd_sc_hd__nand2_1 g115 (.A(n39),
    .B(n81),
    .Y(n123));
 sky130_fd_sc_hd__nand2_1 g116 (.A(n39),
    .B(n123),
    .Y(n124));
 sky130_fd_sc_hd__nand2_1 g117 (.A(n81),
    .B(n123),
    .Y(n125));
 sky130_fd_sc_hd__nand2_1 g118 (.A(n124),
    .B(n125),
    .Y(n126));
 sky130_fd_sc_hd__nand2_1 g119 (.A(n126),
    .B(n122),
    .Y(n127));
 sky130_fd_sc_hd__nand2_1 g12 (.A(a[1]),
    .B(b[2]),
    .Y(n20));
 sky130_fd_sc_hd__nand2_1 g120 (.A(n126),
    .B(n127),
    .Y(n128));
 sky130_fd_sc_hd__nand2_1 g121 (.A(n122),
    .B(n127),
    .Y(n129));
 sky130_fd_sc_hd__nand2_1 g122 (.A(n128),
    .B(n129),
    .Y(p[6]));
 sky130_fd_sc_hd__nand2_1 g123 (.A(n123),
    .B(n127),
    .Y(p[7]));
 sky130_fd_sc_hd__inv_1 g13 (.A(n20),
    .Y(n21));
 sky130_fd_sc_hd__nand2_1 g14 (.A(a[1]),
    .B(b[3]),
    .Y(n22));
 sky130_fd_sc_hd__inv_1 g15 (.A(n22),
    .Y(n23));
 sky130_fd_sc_hd__nand2_1 g16 (.A(a[2]),
    .B(b[0]),
    .Y(n24));
 sky130_fd_sc_hd__inv_1 g17 (.A(n24),
    .Y(n25));
 sky130_fd_sc_hd__nand2_1 g18 (.A(a[2]),
    .B(b[1]),
    .Y(n26));
 sky130_fd_sc_hd__inv_1 g19 (.A(n26),
    .Y(n27));
 sky130_fd_sc_hd__nand2_1 g2 (.A(a[0]),
    .B(b[1]),
    .Y(n10));
 sky130_fd_sc_hd__nand2_1 g20 (.A(a[2]),
    .B(b[2]),
    .Y(n28));
 sky130_fd_sc_hd__inv_1 g21 (.A(n28),
    .Y(n29));
 sky130_fd_sc_hd__nand2_1 g22 (.A(a[2]),
    .B(b[3]),
    .Y(n30));
 sky130_fd_sc_hd__inv_1 g23 (.A(n30),
    .Y(n31));
 sky130_fd_sc_hd__nand2_1 g24 (.A(a[3]),
    .B(b[0]),
    .Y(n32));
 sky130_fd_sc_hd__inv_1 g25 (.A(n32),
    .Y(n33));
 sky130_fd_sc_hd__nand2_1 g26 (.A(a[3]),
    .B(b[1]),
    .Y(n34));
 sky130_fd_sc_hd__inv_1 g27 (.A(n34),
    .Y(n35));
 sky130_fd_sc_hd__nand2_1 g28 (.A(a[3]),
    .B(b[2]),
    .Y(n36));
 sky130_fd_sc_hd__inv_1 g29 (.A(n36),
    .Y(n37));
 sky130_fd_sc_hd__inv_1 g3 (.A(n10),
    .Y(n11));
 sky130_fd_sc_hd__nand2_1 g30 (.A(a[3]),
    .B(b[3]),
    .Y(n38));
 sky130_fd_sc_hd__inv_1 g31 (.A(n38),
    .Y(n39));
 sky130_fd_sc_hd__nand2_1 g32 (.A(n15),
    .B(n21),
    .Y(n40));
 sky130_fd_sc_hd__nand2_1 g33 (.A(n15),
    .B(n40),
    .Y(n41));
 sky130_fd_sc_hd__nand2_1 g34 (.A(n21),
    .B(n40),
    .Y(n42));
 sky130_fd_sc_hd__nand2_1 g35 (.A(n41),
    .B(n42),
    .Y(n43));
 sky130_fd_sc_hd__inv_1 g36 (.A(n40),
    .Y(n44));
 sky130_fd_sc_hd__nand2_1 g37 (.A(n23),
    .B(n29),
    .Y(n45));
 sky130_fd_sc_hd__nand2_1 g38 (.A(n23),
    .B(n45),
    .Y(n46));
 sky130_fd_sc_hd__nand2_1 g39 (.A(n29),
    .B(n45),
    .Y(n47));
 sky130_fd_sc_hd__nand2_1 g4 (.A(a[0]),
    .B(b[2]),
    .Y(n12));
 sky130_fd_sc_hd__nand2_1 g40 (.A(n46),
    .B(n47),
    .Y(n48));
 sky130_fd_sc_hd__inv_1 g41 (.A(n45),
    .Y(n49));
 sky130_fd_sc_hd__nand2_1 g42 (.A(n13),
    .B(n19),
    .Y(n50));
 sky130_fd_sc_hd__nand2_1 g43 (.A(n13),
    .B(n50),
    .Y(n51));
 sky130_fd_sc_hd__nand2_1 g44 (.A(n19),
    .B(n50),
    .Y(n52));
 sky130_fd_sc_hd__nand2_1 g45 (.A(n51),
    .B(n52),
    .Y(n53));
 sky130_fd_sc_hd__inv_1 g46 (.A(n50),
    .Y(n54));
 sky130_fd_sc_hd__nand2_1 g47 (.A(n27),
    .B(n33),
    .Y(n55));
 sky130_fd_sc_hd__nand2_1 g48 (.A(n27),
    .B(n55),
    .Y(n56));
 sky130_fd_sc_hd__nand2_1 g49 (.A(n33),
    .B(n55),
    .Y(n57));
 sky130_fd_sc_hd__inv_1 g5 (.A(n12),
    .Y(n13));
 sky130_fd_sc_hd__nand2_1 g50 (.A(n56),
    .B(n57),
    .Y(n58));
 sky130_fd_sc_hd__nand2_1 g51 (.A(n58),
    .B(n54),
    .Y(n59));
 sky130_fd_sc_hd__nand2_1 g52 (.A(n58),
    .B(n59),
    .Y(n60));
 sky130_fd_sc_hd__nand2_1 g53 (.A(n54),
    .B(n59),
    .Y(n61));
 sky130_fd_sc_hd__nand2_1 g54 (.A(n60),
    .B(n61),
    .Y(n62));
 sky130_fd_sc_hd__nand2_1 g55 (.A(n55),
    .B(n59),
    .Y(n63));
 sky130_fd_sc_hd__nand2_1 g56 (.A(n35),
    .B(n44),
    .Y(n64));
 sky130_fd_sc_hd__nand2_1 g57 (.A(n35),
    .B(n64),
    .Y(n65));
 sky130_fd_sc_hd__nand2_1 g58 (.A(n44),
    .B(n64),
    .Y(n66));
 sky130_fd_sc_hd__nand2_1 g59 (.A(n65),
    .B(n66),
    .Y(n67));
 sky130_fd_sc_hd__nand2_1 g6 (.A(a[0]),
    .B(b[3]),
    .Y(n14));
 sky130_fd_sc_hd__nand2_1 g60 (.A(n67),
    .B(n48),
    .Y(n68));
 sky130_fd_sc_hd__nand2_1 g61 (.A(n67),
    .B(n68),
    .Y(n69));
 sky130_fd_sc_hd__nand2_1 g62 (.A(n48),
    .B(n68),
    .Y(n70));
 sky130_fd_sc_hd__nand2_1 g63 (.A(n69),
    .B(n70),
    .Y(n71));
 sky130_fd_sc_hd__nand2_1 g64 (.A(n64),
    .B(n68),
    .Y(n72));
 sky130_fd_sc_hd__nand2_1 g65 (.A(n31),
    .B(n37),
    .Y(n73));
 sky130_fd_sc_hd__nand2_1 g66 (.A(n31),
    .B(n73),
    .Y(n74));
 sky130_fd_sc_hd__nand2_1 g67 (.A(n37),
    .B(n73),
    .Y(n75));
 sky130_fd_sc_hd__nand2_1 g68 (.A(n74),
    .B(n75),
    .Y(n76));
 sky130_fd_sc_hd__nand2_1 g69 (.A(n76),
    .B(n49),
    .Y(n77));
 sky130_fd_sc_hd__inv_1 g7 (.A(n14),
    .Y(n15));
 sky130_fd_sc_hd__nand2_1 g70 (.A(n76),
    .B(n77),
    .Y(n78));
 sky130_fd_sc_hd__nand2_1 g71 (.A(n49),
    .B(n77),
    .Y(n79));
 sky130_fd_sc_hd__nand2_1 g72 (.A(n78),
    .B(n79),
    .Y(n80));
 sky130_fd_sc_hd__nand2_1 g73 (.A(n73),
    .B(n77),
    .Y(n81));
 sky130_fd_sc_hd__nand2_1 g74 (.A(n11),
    .B(n17),
    .Y(n82));
 sky130_fd_sc_hd__nand2_1 g75 (.A(n11),
    .B(n82),
    .Y(n83));
 sky130_fd_sc_hd__nand2_1 g76 (.A(n17),
    .B(n82),
    .Y(n84));
 sky130_fd_sc_hd__nand2_1 g77 (.A(n83),
    .B(n84),
    .Y(p[1]));
 sky130_fd_sc_hd__inv_1 g78 (.A(n82),
    .Y(n86));
 sky130_fd_sc_hd__nand2_1 g79 (.A(n25),
    .B(n86),
    .Y(n87));
 sky130_fd_sc_hd__nand2_1 g8 (.A(a[1]),
    .B(b[0]),
    .Y(n16));
 sky130_fd_sc_hd__nand2_1 g80 (.A(n25),
    .B(n87),
    .Y(n88));
 sky130_fd_sc_hd__nand2_1 g81 (.A(n86),
    .B(n87),
    .Y(n89));
 sky130_fd_sc_hd__nand2_1 g82 (.A(n88),
    .B(n89),
    .Y(n90));
 sky130_fd_sc_hd__nand2_1 g83 (.A(n90),
    .B(n53),
    .Y(n91));
 sky130_fd_sc_hd__nand2_1 g84 (.A(n90),
    .B(n91),
    .Y(n92));
 sky130_fd_sc_hd__nand2_1 g85 (.A(n53),
    .B(n91),
    .Y(n93));
 sky130_fd_sc_hd__nand2_1 g86 (.A(n92),
    .B(n93),
    .Y(p[2]));
 sky130_fd_sc_hd__nand2_1 g87 (.A(n87),
    .B(n91),
    .Y(n95));
 sky130_fd_sc_hd__nand2_1 g88 (.A(n43),
    .B(n62),
    .Y(n96));
 sky130_fd_sc_hd__nand2_1 g89 (.A(n43),
    .B(n96),
    .Y(n97));
 sky130_fd_sc_hd__inv_1 g9 (.A(n16),
    .Y(n17));
 sky130_fd_sc_hd__nand2_1 g90 (.A(n62),
    .B(n96),
    .Y(n98));
 sky130_fd_sc_hd__nand2_1 g91 (.A(n97),
    .B(n98),
    .Y(n99));
 sky130_fd_sc_hd__nand2_1 g92 (.A(n99),
    .B(n95),
    .Y(n100));
 sky130_fd_sc_hd__nand2_1 g93 (.A(n99),
    .B(n100),
    .Y(n101));
 sky130_fd_sc_hd__nand2_1 g94 (.A(n95),
    .B(n100),
    .Y(n102));
 sky130_fd_sc_hd__nand2_1 g95 (.A(n101),
    .B(n102),
    .Y(p[3]));
 sky130_fd_sc_hd__nand2_1 g96 (.A(n96),
    .B(n100),
    .Y(n104));
 sky130_fd_sc_hd__nand2_1 g97 (.A(n63),
    .B(n71),
    .Y(n105));
 sky130_fd_sc_hd__nand2_1 g98 (.A(n63),
    .B(n105),
    .Y(n106));
 sky130_fd_sc_hd__nand2_1 g99 (.A(n71),
    .B(n105),
    .Y(n107));
endmodule
