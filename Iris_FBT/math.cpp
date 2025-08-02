#include "math.h"

namespace IrisFBT {
    vr::HmdQuaternion_t mRot2Quat(Mat4x4 m) {
        vr::HmdQuaternion_t q{ };

        q.w = sqrt(fmax(0, 1 + m.m[0][0] + m.m[1][1] + m.m[2][2])) / 2;
        q.x = sqrt(fmax(0, 1 + m.m[0][0] - m.m[1][1] - m.m[2][2])) / 2;
        q.y = sqrt(fmax(0, 1 - m.m[0][0] + m.m[1][1] - m.m[2][2])) / 2;
        q.z = sqrt(fmax(0, 1 - m.m[0][0] - m.m[1][1] + m.m[2][2])) / 2;

        q.x = copysign(q.x, m.m[2][1] - m.m[1][2]);
        q.y = copysign(q.y, m.m[0][2] - m.m[2][0]);
        q.z = copysign(q.z, m.m[1][0] - m.m[0][1]);

        return q;
    }

    Vector3::Vector3() : v{ 0, 0, 0 } {}
    Vector3::Vector3(double x, double y, double z) : v{ x, y, z } {}
    Vector3::Vector3(json& data)
    {
        for (int i = 0; i < 3; ++i) { // Row of result matrix
            v[i] = data[i][3].get<double>();
        }
    }
    Vector3::Vector3(vr::HmdMatrix34_t & mat) : v{ mat.m[0][3], mat.m[1][3], mat.m[2][3], } {}
    Vector3 Vector3::operator*(double d) const {
        return Vector3(v[0] * d, v[1] * d, v[2] * d);
    }
    Vector3 Vector3::operator*=(double d)
    {
        v[0] *= d;
        v[1] *= d;
        v[2] *= d;
        return *this;
    }
    Vector3 Vector3::operator/(double d) const
    {
        return Vector3(v[0] / d, v[1] / d, v[2] / d);
    }
    Vector3 Vector3::operator/=(double d)
    {
        v[0] /= d;
        v[1] /= d;
        v[2] /= d;
        return *this;
    }
    Vector3 Vector3::operator+(const Vector3 a) const
    {
        return Vector3(v[0] + a.v[0], v[1] + a.v[1], v[2] + a.v[2]);
    }
    Vector3 Vector3::operator+=(const Vector3 a)
    {
        v[0] += a.v[0];
        v[1] += a.v[1];
        v[2] += a.v[2];
        return *this;
    }
    Vector3 Vector3::operator-(const Vector3 a) const
    {
        return Vector3(v[0] - a.v[0], v[1] - a.v[1], v[2] - a.v[2]);
    }
    Vector3 Vector3::operator-() const
    {
        return Vector3(-v[0], -v[1], -v[2]);
    }
    Vector3 Vector3::operator-=(const Vector3 a)
    {
        v[0] -= a.v[0];
        v[1] -= a.v[1];
        v[2] -= a.v[2];
        return *this;
    }
    double Vector3::operator*(const Vector3 a) const {
        return dot(*this, a);
    }
    double Vector3::dot(const Vector3 a, const Vector3 b)
    {
        return a.v[0] * b.v[0] + a.v[1] * b.v[1] + a.v[2] * b.v[2];
    }
    Vector3 Vector3::cross(const Vector3 a, const Vector3 b)
    {
        return Vector3(a.v[1] * b.v[2] - a.v[2] * b.v[1],
                       a.v[2] * b.v[0] - a.v[0] * b.v[2],
                       a.v[0] * b.v[1] - a.v[1] * b.v[0]);
    }
    Vector3 Vector3::project(const Vector3 a, const Vector3 b)
    {
        return b * (dot(a, b) / dot(b, b));
    }
    Vector3 Vector3::reject(const Vector3 a, const Vector3 b)
    {
        return a - project(a, b);
    }
    Vector3 Vector3::normalized() const
    {
        return *this / length();
    }
    double Vector3::length() const {
        return sqrt(dot(*this, *this));
    }
    string Vector3::to_string() const
    {
        return '(' + std::to_string(v[0]) + ", " + std::to_string(v[1]) + ", " + std::to_string(v[2]) + ')';
    }


    Mat4x4::Mat4x4() {

        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = i == j;
            }
        }
    }
    Mat4x4::Mat4x4(int) : m{ 0 } {}
    Mat4x4::Mat4x4(json& data) {
        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                m[i][j] = data[i][j].get<double>();
            }
        }
    }
    Mat4x4::Mat4x4(const Vector3 x, const Vector3 y, const Vector3 z, const Vector3 p)
    {
        for (int i = 0; i < 3; i++) {
            m[i][0] = x.v[i];
            m[i][1] = y.v[i];
            m[i][2] = z.v[i];
            m[i][3] = p.v[i];
        }
        m[3][0] = 0;
        m[3][1] = 0;
        m[3][2] = 0;
        m[3][3] = 1;
    }
    Mat4x4 Mat4x4::operator*(const Mat4x4 a) const
    {
        Mat4x4 res(0);
        for (int i = 0; i < 4; ++i) { // Row of result matrix
            for (int j = 0; j < 4; ++j) { // Column of result matrix
                for (int k = 0; k < 4; ++k) { // Elements for dot product
                    res.m[i][j] += this->m[i][k] * a.m[k][j];
                }
            }
        }
        return res;
    }
    Vector3 Mat4x4::operator*(const Vector3 a) const
    {
        Vector3 res;
        for (int i = 0; i < 3; i++) {
            for (int k = 0; k < 3; ++k) {
                res.v[i] += this->m[i][k] * a.v[k];
            }
            res.v[i] += this->m[i][3];
        }
        return res;
    }
    Mat4x4 Mat4x4::inverse() const
    {
        Mat4x4 inv;

        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                inv.m[i][j] = m[j][i];

        Vector3 pos(m[0][3], m[1][3], m[2][3]);
        pos = inv * pos;
        inv.m[0][3] = -pos.v[0];
        inv.m[1][3] = -pos.v[1];
        inv.m[2][3] = -pos.v[2];
        return inv;
    }
    Mat4x4 Mat4x4::get_rotation() const
    {
        Mat4x4 res;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                res.m[i][j] = m[i][j];
        return res;
    }
    Vector3 Mat4x4::get_vector(int i) const
    {
        return Vector3(m[0][i], m[1][i], m[2][i]);
    }
    string Mat4x4::to_string() const
    {
        string str = "[\n";
        for (int i = 0; i < 4; i++) {
            str += " [";
            for (int j = 0; j < 4; j++)
                str += std::to_string(m[i][j]) + ", ";
            str += "]\n";
        }
        return str + ']';
    }
}