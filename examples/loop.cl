// Simple program demonstrating variables, if/else, while, print, and comments
let x = 0;
let sum = 0;

while (x < 10) {
  sum = sum + x;
  x = x + 1;
}

if (sum >= 45) {
  print("sum is " + sum);
} else {
  print("unexpected");
}
