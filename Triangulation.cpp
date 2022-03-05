#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <stdio.h>
#include <vector>
#include <queue>
#include <list>
#include <algorithm>
#include <memory>

using namespace std;

namespace py = pybind11;

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

class Triangle{

    public:
        Triangle() = delete;
        Triangle(int a1,int a2, int b1, int b2, int c1, int c2):nbh(3), x(Point(a1,a2)), y(Point(b1,b2)), z(Point(c1,c2)){};
        Triangle(Point a, Point b, Point c): nbh(3), x(a), y(b), z(c){};    
        ~Triangle() = default;
        vector<shared_ptr<Triangle>> nbh; 

        vector<Point> get_pts() const;   
        void set_pts(const Point& a, const Point& b, const Point& c);
        std::list<int> get_points(){return {x[0],x[1],y[0],y[1],z[0],z[1]};}
        std::list<int> get_nbh_points();
        
        bool pt_contained(int p1, int p2);
        int nbh_position(shared_ptr<Triangle> A);
        Point nbh_point(int i);

        list<int> get_triangle_via_point(int x, int y, shared_ptr<Triangle> this_ptr);
        void initialize(shared_ptr<Triangle> this_ptr, int h, int w);                     
        void split(int x, int y, shared_ptr<Triangle> this_ptr);
        shared_ptr<Triangle> add_point(int x, int y, shared_ptr<Triangle> this_ptr);
        bool delaunay_prop(int i);       
        void flip(int i, shared_ptr<Triangle> this_ptr);
        void re_delaunay_prop( shared_ptr<Triangle> this_ptr);                                

    private:
        Point x,y,z;
          

};


std::list<int> Triangle::get_nbh_points(){
    list<int> list({x[0],x[1],y[0],y[1],z[0],z[1]});
    for(int i =0 ; i<3; i++){
        if(nbh[i]){
            list.push_back(nbh[i]->x[0]);
            list.push_back(nbh[i]->x[1]);
            list.push_back(nbh[i]->y[0]);
            list.push_back(nbh[i]->y[1]);
            list.push_back(nbh[i]->z[0]);
            list.push_back(nbh[i]->z[1]);
        }
    }
    return list;
}

//Get-function that returns the vertices of the triangle
vector<Point> Triangle::get_pts() const{
    return vector<Point>({x,y,z});
}

//Set-function for the vertices (orientation - counterclockwise)
void Triangle::set_pts(const Point& a, const Point& b, const Point& c){
    //assert - a,b,c are oriented counterclockwise
    x = a;
    y = b;
    z = c;
}

//Returns the position of a given neighbor
int Triangle::nbh_position(shared_ptr<Triangle> A){
    for(int i = 0; i<3;i++){
        if(nbh[i] == A)
            return i;
    }
    return -1;  //case: not a neighbor 
}

//Returns the remaining point for a given neighbor
Point Triangle::nbh_point(int i){
    if(nbh[i]){
        auto pts = nbh[i]->get_pts();
        for(int j=0; j < 3; j ++){
            if(pts[j] != x && pts[j] != y && pts[j] != z)
                return pts[j];
        }
    }
    return Point(0,0);  //case: there is no ith neighbor   
}

//Checks if a point is inside the given triangle
bool Triangle::pt_contained(int p1, int p2){
    Point p(p1,p2);
    Point nxy((y - x)[1], -(y - x)[0]);
    Point nyz((z - y)[1], -(z - y)[0]);
    Point nzx((x - z)[1], -(x - z)[0]);
    return nxy*(p-x) < 0 &&  nyz*(p-y) < 0 && nzx*(p-z) < 0;
}

// initalizes triangles attached counter clockwise wrt the centerpoint z1,z2
void Triangle::initialize(shared_ptr<Triangle> this_ptr, int h, int w){
    auto E = make_shared<Triangle>(Triangle(-1, -1, w +1, -1, w +1, h+1));
    this_ptr->nbh[0] = E;
    E->nbh[2] = this_ptr; 
    return;
}

//Replaces the given triangle that contains a given point with three new triangles
void Triangle::split(int x, int y, shared_ptr<Triangle> this_ptr){
    // assert (!pt_contained(x,y))
    auto v = get_pts();
    auto B = nbh[1];
    auto C = nbh[2];

    this_ptr->set_pts(v[0], v[1], Point(x,y));
    auto D = make_shared<Triangle>(Triangle(v[1],v[2], Point(x,y)));
    auto E = make_shared<Triangle>(Triangle(Point(x,y), v[2], v[0]));

    D->nbh[0] = B;
    D->nbh[1] = E;
    D->nbh[2] = this_ptr;

    E->nbh[0] = D;
    E->nbh[1] = C;
    E->nbh[2] = this_ptr;

    nbh[1] = D;
    nbh[2] = E;

    if(B != nullptr)
        B->nbh[B->nbh_position(this_ptr)] = D;
    if(C != nullptr)
        C->nbh[C->nbh_position(this_ptr)] = E;
    return;
}

//Adds a new point to the triangulation
shared_ptr<Triangle> Triangle::add_point(int x, int y, shared_ptr<Triangle> this_ptr){
    vector<shared_ptr<Triangle>> Trgls = {this_ptr};
    queue<shared_ptr<Triangle>> Cnddts;
    Cnddts.push( this_ptr );
    while(Cnddts.size() != 0){
        if(Cnddts.front()->pt_contained(x,y)){
            Cnddts.front()->split(x,y,Cnddts.front());
            return Cnddts.front();
        }
        else{
            for(int i = 0; i<3; i++){
                if(find(Trgls.begin(),Trgls.end(),Cnddts.front()->nbh[i]) == Trgls.end() && Cnddts.front()->nbh[i] != nullptr){
                    Trgls.push_back(Cnddts.front()->nbh[i]);
                    Cnddts.push(Cnddts.front()->nbh[i]);
                }
            }
            Cnddts.pop();
        }
    }
    return nullptr;
}

//Adds a new point to the triangulation
list<int> Triangle::get_triangle_via_point(int x, int y, shared_ptr<Triangle> this_ptr){
    vector<shared_ptr<Triangle>> Trgls = {this_ptr};
    queue<shared_ptr<Triangle>> Cnddts;
    Cnddts.push( this_ptr );
    while(Cnddts.size() != 0){
        if(Cnddts.front()->pt_contained(x,y)){
            return {Cnddts.front()->get_pts()[0][0],Cnddts.front()->get_pts()[0][1], Cnddts.front()->get_pts()[1][0],Cnddts.front()->get_pts()[1][1], Cnddts.front()->get_pts()[2][0],Cnddts.front()->get_pts()[2][1] };
        }
        else{
            for(int i = 0; i<3; i++){
                if(find(Trgls.begin(),Trgls.end(),Cnddts.front()->nbh[i]) == Trgls.end() && Cnddts.front()->nbh[i] != nullptr){
                    Trgls.push_back(Cnddts.front()->nbh[i]);
                    Cnddts.push(Cnddts.front()->nbh[i]);
                }
            }
            Cnddts.pop();
        }
    }
    return list<int>();
}

//checks if the delaunay property is satisfied wrt. the given and the ith triangle
bool Triangle::delaunay_prop(int i){
    if(nbh[i] == nullptr)   //trivial case 
        return true;
    Point D = nbh_point(i);
    int k = (i+1) % 3;
    int l = (i+2) % 3;
    auto x = get_pts();
    int mat[3][3] = {   {x[k][0] - D[0], x[k][1] - D[1], (x[k][0] - D[0])*(x[k][0] - D[0]) + (x[k][1] - D[1])*(x[k][1] - D[1])},
                        {x[l][0] - D[0], x[l][1] - D[1], (x[l][0] - D[0])*(x[l][0] - D[0]) + (x[l][1] - D[1])*(x[l][1] - D[1])},
                        {x[i][0] - D[0], x[i][1] - D[1], (x[i][0] - D[0])*(x[i][0] - D[0]) + (x[i][1] - D[1])*(x[i][1] - D[1])}
                    };
    if( det(mat) > 0)
        return false;
    return true;
}

//Restores the delaunay property locally
void Triangle::flip(int i, shared_ptr<Triangle> this_ptr){
    int m = nbh[i]->nbh_position(this_ptr);

    Point a = get_pts()[(i+1) % 3];
    Point b = get_pts()[(i+2) % 3];
    Point c = get_pts()[i];
    Point d = nbh_point(i);

    auto T_ab = nbh[(i+1) % 3];
    auto T_bc = nbh[(i+2) % 3];
    auto T_cd = nbh[i]->nbh[(m+1) % 3];
    auto T_da = nbh[i]->nbh[(m+2) % 3];

    nbh[i]->set_pts(a,b,d);
    nbh[i]->nbh[0] = T_ab;
    nbh[i]->nbh[1] = this_ptr;
    nbh[i]->nbh[2] = T_da;

    if(T_ab != nullptr)
        T_ab->nbh[T_ab->nbh_position(this_ptr)] = nbh[i];
    if(T_cd != nullptr)
        T_cd->nbh[T_cd->nbh_position(nbh[i])] = this_ptr;

    this_ptr->set_pts(d,b,c);
    this_ptr->nbh[0] = nbh[i];
    this_ptr->nbh[1] = T_bc;
    this_ptr->nbh[2] = T_cd;

    return;
}

//Restores the delaunay property globally
void Triangle::re_delaunay_prop( shared_ptr<Triangle> this_ptr ){
    vector<shared_ptr<Triangle>> Trgls = {this_ptr};
    queue<shared_ptr<Triangle>> Cnddts;
    Cnddts.push( this_ptr );
    while(Cnddts.size() != 0){
        for(int j = 0; j < 3; j++){
            if(!Cnddts.front()->delaunay_prop(j)){
                for(int i = 0; i<3; i++){
                    if(find(Trgls.begin(),Trgls.end(),Cnddts.front()->nbh[i]) == Trgls.end() && Cnddts.front()->nbh[i] != nullptr){
                        Trgls.push_back(Cnddts.front()->nbh[i]);
                        Cnddts.push(Cnddts.front()->nbh[i]);
                    }
                }
                for(int i = 0; i<3; i++){
                    if(find(Trgls.begin(),Trgls.end(),Cnddts.front()->nbh[j]->nbh[i]) == Trgls.end() && Cnddts.front()->nbh[j]->nbh[i] != nullptr){
                        Trgls.push_back(Cnddts.front()->nbh[j]->nbh[i]);
                        Cnddts.push(Cnddts.front()->nbh[j]->nbh[i]);
                    }
                }
                Cnddts.front()->flip(j, Cnddts.front());
                j = 3;
            }
        }
        Cnddts.pop();
    }
    return;
}

PYBIND11_MODULE(Triangulation, m){
    py::class_<Point>(m, "Point")
        .def(py::init<int, int>())
        .def(py::init<const Point&>())
        .def(py::self += py::self)
        .def(py::self -= py::self);

    py::class_<Triangle, std::shared_ptr<Triangle>>(m, "Triangle")
        .def(py::init<int,int,int,int,int,int>())
        .def(py::init<Point,Point,Point>())
        .def_readwrite("nbh", &Triangle::nbh)
        .def("add_point", &Triangle::add_point)
        .def("initialize", &Triangle::initialize)
        .def("re_delaunay_prop", &Triangle::re_delaunay_prop)
        .def("get_points", &Triangle::get_points)
        .def("get_nbh", &Triangle::get_nbh_points)
        .def("get_triangle_via_point", &Triangle::get_triangle_via_point);


}