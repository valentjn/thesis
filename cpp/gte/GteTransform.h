// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.2 (2014/12/13)

#pragma once

#include <gte/GteLogger.h>
#include <gte/GteMatrix4x4.h>
#include <gte/GteRotation.h>
#include <gte/GteVector3.h>
#include <gte/GTEngineDEF.h>
#include <cassert>

// Verify that the inputs to SetAxisAngle, SetRotation, and SetScale are
// valid.
//#define GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT

// This class is a convenient wrapper for invertible affine matrices M formed
// by rotation, translation, and nonzero uniform scaling.  As block matrices,
// the format of M depends on your matrix-vector multiplication convention.
//   [GTE_USE_MAT_VEC]  M = {{R*s,u},{0,1}}
//   [GTE_USE_VEC_MAT]  M = {{s*R,0},{v,1}}
// where R is a 3x3 rotation matrix, s is a nonzero scalar, u is a 3x1
// translation, and v is a 1x3 translation.  The 0 blocks are 3x1 or 1x3 and
// the 1 block is 1x1.  The product of two Transform matrices is a Transform
// matrix.  When GTE_USE_MAT_VEC is active,
//   M0 = {{R0*s0,u0},{0,1}}, M1 = {{R1*s1,u1},{0,1}}
//   M0*M1 = {{(R0*R1)*(s0*s1),R0*s0*u1+u0},{0,1}}
// When GTE_USE_VEC_MAT is active,
//   M0 = {{s0*R0,0},{u0,1}}, M1 = {{s1*R1,0},{u1,1}}
//   M0*M1 = {{(s0*s1)*(R0*R1),0},{Transpose(u0)*s1*R1+u1,1}}

namespace gte
{

template <typename Real>
class Transform : public Matrix4x4<Real>
{
public:
    // Construction and destruction.  The default constructor generates the
    // identity transformation.
    ~Transform();
    Transform();
    Transform(Transform const& transform);

    // Assignment.
    Transform& operator=(Transform const& transform);

    // Set the transformation to the identity.
    void SetIdentity();

    // The quaternion is unit length.
    void SetQuaternion (Quaternion<Real> const& q);
    Quaternion<Real> GetQuaternion() const;

    // The axis is unit length and the angle is in radians.
    void SetAxisAngle(AxisAngle<4,Real> const& axisAngle);
    AxisAngle<4,Real> GetAxisAngle() const;

    // The Euler angles are in radians.  The GetEulerAngles function
    // expects the eulerAngles.axis[] values to be set to the axis order
    // you want.
    void SetEulerAngles(EulerAngles<Real> const& eulerAngles);
    void GetEulerAngles(EulerAngles<Real>& eulerAngles) const;

    // The caller must ensure that the input to SetRotation is a rotation
    // matrix.
    void SetRotation(Matrix4x4<Real> const& rotation);
    Matrix4x4<Real> GetRotation() const;

    // The scale is a nonzero number.
    void SetScale(Real scale);
    Real GetScale() const;

    // No constraints exist for the translation components.  The third Set*
    // function uses only the first three components of 'translation'.  The
    // Get*W* functions store the translation in the first three components
    // of the output.  The fourth component is w=0 or w=1 depending on
    // which function you call.
    void SetTranslation(Real x0, Real x1, Real x2);
    void SetTranslation(Vector3<Real> const& translation);
    void SetTranslation(Vector4<Real> const& translation);
    Vector3<Real> GetTranslation() const;
    Vector4<Real> GetTranslationW0() const;
    Vector4<Real> GetTranslationW1() const;

    // Multiplication of transforms.  M0 is 'this', M1 is 'transform', the
    // function returns M0*M1.
    Transform<Real> operator*(Transform<Real> const& transform) const;

private:
    // Compute the base-class Matrix4x4<Real> from the channels.
    void UpdateMatrix();

    Quaternion<Real> mQuaternion;
    Real mTranslation[3], mScale;

#if defined(GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT)
    static bool IsRotation(Matrix4x4<Real> const& rotate, Real epsilon);
    static bool IsUnitLength(Vector4<Real> const& axis, Real epsilon);
#endif
};

//----------------------------------------------------------------------------
template <typename Real>
Transform<Real>::~Transform()
{
}
//----------------------------------------------------------------------------
template <typename Real>
Transform<Real>::Transform()
{
    SetIdentity();
}
//----------------------------------------------------------------------------
template <typename Real>
Transform<Real>::Transform(Transform const& transform)
{
    *this = transform;
}
//----------------------------------------------------------------------------
template <typename Real>
Transform<Real>& Transform<Real>::operator=(Transform<Real> const& transform)
{
    Matrix4x4<Real>::operator=(transform);
    mQuaternion = transform.mQuaternion;
    mTranslation[0] = transform.mTranslation[0];
    mTranslation[1] = transform.mTranslation[1];
    mTranslation[2] = transform.mTranslation[2];
    mScale = transform.mScale;
    return *this;
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetIdentity()
{
    this->MakeIdentity();
    mQuaternion = Quaternion<Real>::Identity();
    mTranslation[0] = (Real)0;
    mTranslation[1] = (Real)0;
    mTranslation[2] = (Real)0;
    mScale = (Real)1;
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetQuaternion(Quaternion<Real> const& q)
{
    mQuaternion = q;
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
Quaternion<Real> Transform<Real>::GetQuaternion() const
{
    return mQuaternion;
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetAxisAngle(AxisAngle<4, Real> const& axisAngle)
{
#if defined(GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT)
    LogAssert(IsUnitLength(axisAngle.axis, (Real)1e-05),
        "Axis must be unit length.");
#endif

    mQuaternion = Rotation<4, Real>(axisAngle);
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
AxisAngle<4, Real> Transform<Real>::GetAxisAngle() const
{
    return Rotation<4, Real>(mQuaternion);
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetEulerAngles(EulerAngles<Real> const& eulerAngles)
{
    mQuaternion = Rotation<4, Real>(eulerAngles);
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::GetEulerAngles(EulerAngles<Real>& eulerAngles) const
{
    eulerAngles = Rotation<4, Real>(mQuaternion)(eulerAngles.axis[0],
        eulerAngles.axis[1], eulerAngles.axis[2]);
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetRotation(Matrix4x4<Real> const& rotation)
{
#if defined(GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT)
    LogAssert(IsRotation(rotation, (Real)1e-5),
        "The matrix is not a rotation.");
#endif

    mQuaternion = Rotation<4, Real>(rotation);
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
Matrix4x4<Real> Transform<Real>::GetRotation() const
{
    return (Matrix<4, 4, Real>)Rotation<4, Real>(mQuaternion);
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetScale(Real scale)
{
#if defined(GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT)
    LogAssert(scale != (Real)0, "The scale must be nonzero.");
#endif

    mScale = scale;
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
Real Transform<Real>::GetScale() const
{
    return mScale;
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetTranslation(Real x0, Real x1, Real x2)
{
    mTranslation[0] = x0;
    mTranslation[1] = x1;
    mTranslation[2] = x2;
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetTranslation(Vector3<Real> const& translation)
{
    mTranslation[0] = translation[0];
    mTranslation[1] = translation[1];
    mTranslation[2] = translation[2];
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::SetTranslation(Vector4<Real> const& translation)
{
    mTranslation[0] = translation[0];
    mTranslation[1] = translation[1];
    mTranslation[2] = translation[2];
    UpdateMatrix();
}
//----------------------------------------------------------------------------
template <typename Real>
Vector3<Real> Transform<Real>::GetTranslation() const
{
    return Vector3<Real>{ mTranslation[0], mTranslation[1],
        mTranslation[2] };
}
//----------------------------------------------------------------------------
template <typename Real>
Vector4<Real> Transform<Real>::GetTranslationW0() const
{
    return Vector4<Real>{ mTranslation[0], mTranslation[1], mTranslation[2],
        (Real)0 };
}
//----------------------------------------------------------------------------
template <typename Real>
Vector4<Real> Transform<Real>::GetTranslationW1() const
{
    return Vector4<Real>{ mTranslation[0], mTranslation[1], mTranslation[2],
        (Real)1 };
}
//----------------------------------------------------------------------------
template <typename Real>
Transform<Real> Transform<Real>::operator*(Transform<Real> const& transform)
const
{
    Transform<Real> M0M1;
    M0M1.mQuaternion = mQuaternion * transform.mQuaternion;
    M0M1.mScale = mScale * transform.mScale;
#if defined(GTE_USE_MAT_VEC)
    Vector4<Real> trn = Rotate<Real>(mQuaternion,
        mScale * transform.GetTranslationW0()) + GetTranslationW0();
#else
    Vector4<Real> trn = Rotate<Real>(transform.mQuaternion,
        transform.mScale * GetTranslationW0() + transform.GetTranslationW1());
#endif
    M0M1.mTranslation[0] = trn[0];
    M0M1.mTranslation[1] = trn[1];
    M0M1.mTranslation[2] = trn[2];
    M0M1.UpdateMatrix();
    return M0M1;
}
//----------------------------------------------------------------------------
template <typename Real>
void Transform<Real>::UpdateMatrix()
{
    Matrix4x4<Real> rotation =
        (Matrix<4, 4, Real>)Rotation<4, Real>(mQuaternion);
    Matrix4x4<Real>::operator=(mScale*rotation);
#if defined(GTE_USE_MAT_VEC)
    (*this)(0, 3) = mTranslation[0];
    (*this)(1, 3) = mTranslation[1];
    (*this)(2, 3) = mTranslation[2];
#else
    (*this)(3, 0) = mTranslation[0];
    (*this)(3, 1) = mTranslation[1];
    (*this)(3, 2) = mTranslation[2];
#endif
    (*this)(3, 3) = (Real)1;
}
//----------------------------------------------------------------------------
#if defined(GTE_ASSERT_ON_INVALID_TRANSFORM_INPUT)
//----------------------------------------------------------------------------
template <typename Real>
bool Transform<Real>::IsRotation(Matrix4x4<Real> const& rotate, Real epsilon)
{
    Matrix4x4<Real> test =
        MultiplyATB(rotate, rotate) - Matrix4x4<Real>::Identity();

    Real maxError = (Real)0;
    for (int i = 0; i < 16; ++i)
    {
        Real error = test[i];
        if (error > maxError)
        {
            maxError = error;
        }
    }

    return maxError < epsilon;
}
//----------------------------------------------------------------------------
template <typename Real>
bool Transform<Real>::IsUnitLength(Vector4<Real> const& axis,
    Real epsilon)
{
    Real error = std::abs(Length(axis) - (Real)1);
    return error < epsilon;
}
//----------------------------------------------------------------------------
#endif
//----------------------------------------------------------------------------

}
