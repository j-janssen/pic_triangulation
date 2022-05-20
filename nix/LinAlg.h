#ifndef LINEARALGEBRA_H
#define LINEARALGEBRA

// ein neuer kommentar

class Point{

    public:
        Point()                             = delete;
        Point(int a, int b): x(a),y(b){};
        Point(const Point& p)               = default;
        Point& operator=(const Point& p)    = default;
        Point(Point&& p)                    = default;
        Point& operator=(Point&& p)         = default;
        ~Point()                            = default;

        int& operator[](int i);
        Point& operator-=(Point b);
        Point& operator+=(Point b);
        
    private:
        int x,y;

};

bool operator==(Point a, Point b);
bool operator!=(Point a, Point b);
Point operator-(Point a, Point b);
Point operator+(Point a, Point b);
int operator*(Point a, Point b);

int det(int mat[3][3]);

#endif
