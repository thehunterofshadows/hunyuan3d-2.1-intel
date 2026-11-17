// Glue-on encoder mount, millimeters.
$fn = 80;
width = 31.77;
long_rows = [78.39, 81.93];
plate = [92, 42];
base = 2.4;
post = 8;
bore = 4.4;
depth = 7;
eps = 0.02;

module at_posts() {
    for (row = [0, 1], x = [-81.93/2, -81.93/2 + long_rows[row]])
        translate([x,(row-0.5)*width,0]) children();
}

difference() {
    union() {
        translate([-plate.x/2,-plate.y/2,0])
            linear_extrude(base)
                offset(r=2) translate([2,2]) square(plate-[4,4]);
        at_posts() translate([0,0,base-eps]) cylinder(h=post+eps,d=8);
    }
    at_posts() {
        translate([0,0,base+post-depth]) cylinder(h=depth+eps,d=bore);
        translate([0,0,base+post-0.4]) cylinder(h=0.4+eps,d1=bore,d2=5.0);
    }
}
