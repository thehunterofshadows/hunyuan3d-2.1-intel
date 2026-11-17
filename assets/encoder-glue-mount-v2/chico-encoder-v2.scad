// Glue-on encoder mount, millimeters.
$fn = 80;
pitch = [80, 30];
plate = [90, 40];
base = 2.4;
post = 8;
bore = 4.4;
depth = 7;
eps = 0.02;

module at_posts() {
    for (x = [-pitch.x/2, pitch.x/2], y = [-pitch.y/2, pitch.y/2])
        translate([x,y,0]) children();
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
