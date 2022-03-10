/********************************************************/
/*  NAME:   Jörg Janssen                                */
/*  ORGN:   -                                           */
/*  FILE:   Triangle.cpp                                */ 
/*  DATE:   Aug 7th 2021                                */
/********************************************************/

#include "LinAlg.h"

int& Point::operator[](int i){

    if(i == 0) return x;
    return y;
}

Point& Point::operator-=(Point b){
    x -= b[0];
    y -= b[1];
    return *this;
}

Point& Point::operator+=(Point b){
    x += b[0];
    y += b[1];
    return *this;
}

Point operator-(Point a, Point b){
    return a-= b;
}

Point operator+(Point a, Point b){
    return a+= b;
}

int operator*(Point a, Point b){
    return a[0]*b[0] + a[1]*b[1];
}

bool operator==(Point a, Point b){
    return (a[0] == b[0] && a[1]==b[1]);
}

bool operator!=(Point a, Point b){
    return !(a==b);
}

int det(int mat[3][3]){
    int d   = mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1]);
    d       -= mat[1][0] * (mat[0][1] * mat[2][2] - mat[0][2] * mat[2][1]);
    d       += mat[2][0] * (mat[0][1] * mat[1][2] - mat[0][2] * mat[1][1]);     
    return d; 
}