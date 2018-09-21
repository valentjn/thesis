// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/12/13)

#pragma once

#include <gte/GteMatrix4x4.h>
#include <gte/GTEngineDEF.h>

// The camera basis vectors are tested for orthogonality once.  This is useful
// in Debug builds to trap incorrectly specified vectors.
#define GTE_VALIDATE_CAMERA_FRAME_ONCE

namespace gte
{

class GTE_IMPEXP Camera
{
public:
    // Construction.
    Camera(bool isPerspective = true);

    // The camera frame is always in world coordinates.
    //   default position  P = (0, 0,  0; 1)
    //   default direction D = (0, 0, -1; 0)
    //   default up        U = (0, 1,  0; 0)
    //   default right     R = (1, 0,  0; 0)
    void SetFrame(
        Vector4<float> const& position,
        Vector4<float> const& dVector,
        Vector4<float> const& uVector,
        Vector4<float> const& rVector);

    void SetPosition(Vector4<float> const& position);

    void SetAxes(
        Vector4<float> const& dVector,
        Vector4<float> const& uVector,
        Vector4<float> const& rVector);

    void GetFrame(
        Vector4<float>& position,
        Vector4<float>& dVector,
        Vector4<float>& uVector,
        Vector4<float>& rVector) const;

    void GetAxes(
        Vector4<float>& dVector,
        Vector4<float>& uVector,
        Vector4<float>& rVector) const;

    inline Vector4<float> const& GetPosition() const;
    inline Vector4<float> const& GetDVector() const;
    inline Vector4<float> const& GetUVector() const;
    inline Vector4<float> const& GetRVector() const;

    // Access the view matrix of the camera.  If D = (d0,d1,d2),
    // U = (u0,u1,u2), and R = (r0,r1,r2), then the view matrix is
    //   +-                     -+
    //   | r0  r1  r2  -Dot(R,P) |
    //   | u0  u1  u2  -Dot(U,P) |
    //   | d0  d1  d2  -Dot(D,P) |
    //   |  0   0   0          1 |
    //   +-                     -+
    // The view matrix multiplies vectors on its right, viewMat*vector4.
    inline const Matrix4x4<float>& GetViewMatrix() const;

    // The view frustum has parameters [rmin,rmax], [umin,umax], and
    // [dmin,dmax].  The interval [rmin,rmax] is measured in the right
    // direction R.  These are the "left" and "right" frustum values.  The
    // interval [umin,umax] is measured in the up direction U.  These are
    // the "bottom" and "top" values.  The interval [dmin,dmax] is measured
    // in the view direction D.  These are the "near" and "far" values.
    // The frustum values are stored in an array with the following mappings:
    enum
    {
        VF_DMIN     = 0,  // near
        VF_DMAX     = 1,  // far
        VF_UMIN     = 2,  // bottom
        VF_UMAX     = 3,  // top
        VF_RMIN     = 4,  // left
        VF_RMAX     = 5,  // right
        VF_QUANTITY = 6
    };

    // The default view frustum has an up field-of-view of 90 degrees, an
    // aspect ratio of 1, near value 1, and far value 10000.

    inline bool IsPerspective() const;

    // Set the view frustum.  The interval [rmin,rmax] is measured in the
    // right direction R.  These are the "left" and "right" frustum values.
    // The interval [umin,umax] is measured in the up direction U.  These are
    // the "bottom" and "top" values.  The interval [dmin,dmax] is measured
    // in the view direction D.  These are the "near" and "far" values.
    void SetFrustum(float dMin, float dMax, float uMin, float uMax,
        float rMin, float rMax);

    // Set all the view frustum values simultaneously.  The input array must
    // have the order:  dmin, dmax, umin, umax, rmin, rmax.
    void SetFrustum(float const* frustum);

    // Set a symmetric view frustum (umin = -umax, rmin = -rmax) using a field
    // of view in the "up" direction and an aspect ratio "width/height".  The
    // field of view in this function must be specified in degrees and be in
    // the interval (0,180).
    void SetFrustum(float upFovDegrees, float aspectRatio, float dMin,
        float dMax);

    // Get the view frustum.
    void GetFrustum(float& dMin, float& dMax, float& uMin, float& uMax,
        float& rMin, float& rMax) const;

    // Get all the view frustum values simultaneously.
    inline float const* GetFrustum() const;

    // Get the parameters for a symmetric view frustum.  The return value is
    // 'true' iff the current frustum is symmetric, in which case the output
    // parameters are valid.
    bool GetFrustum(float& upFovDegrees, float& aspectRatio, float& dMin,
        float& dMax) const;

    // Get the individual frustum values.
    inline float GetDMin() const;
    inline float GetDMax() const;
    inline float GetUMin() const;
    inline float GetUMax() const;
    inline float GetRMin() const;
    inline float GetRMax() const;

    // Access the projection matrices of the camera.  These matrices map to
    // depths in the interval [0,1].

    // The frustum values are N (near), F (far), B (bottom), T (top),
    // L (left), and R (right).  The various matrices are as follows,
    // shown for GTE_USE_MAT_VEC.  The transpose of these matrices are
    // used for GTE_USE_VEC_MAT.
    //
    // perspective
    //   +-                                               -+
    //   | 2*N/(R-L)  0           -(R+L)/(R-L)  0          |
    //   | 0          2*N/(T-B)   -(T+B)/(T-B)  0          |
    //   | 0          0           F/(F-N)       -N*F/(F-N) |
    //   | 0          0           1             0          |
    //   +-                                               -+
    //
    // orthographic
    //   +-                                       -+
    //   | 2/(R-L)  0  0              -(R+L)/(R-L) |
    //   | 0        2/(T-B)  0        -(T+B)/(T-B) |
    //   | 0        0        1/(F-N)  -N/(F-N)     |
    //   | 0        0        0        1            |
    //   +-                                       -+
    //
    // The projection matrix multiplies vectors on its right, projMat*vector4.

    // The returned matrix is perspective or orthographic depending on the
    // value of mIsPerspective.
    inline Matrix4x4<float> const& GetProjectionMatrix() const;

    // For advanced effects, you might want to set the projection matrix to
    // something other than the standard one.
    inline void SetProjectionMatrix(Matrix4x4<float> const& projMatrix);

    // Support for parallax projection.  You specify a convex quadrilateral
    // viewport.  The points must be in camera coordinates and are ordered
    // counterclockwise as viewed from the eyepoint.  The plane of the
    // quadrilateral is the view plane and has an "extrude" value of 1.  The
    // nearExtrude value is in (0,infinity); this specifies the fraction from
    // the eyepoint to the view plane containing the near-face of the cuboidal
    // view volume.  The farExtrude value is in (nearExtrude,infinity); this
    // specifies the fraction from the eyepoint at which to place the far-face
    // of the cuboidal view volume.
    void SetProjectionMatrix(Vector4<float> const& p00,
        Vector4<float> const& p10, Vector4<float> const& p11,
        Vector4<float> const& p01, float nearExtrude, float farExtrude);

    // The projection-view-world matrix is commonly used in the shader
    // programs to transform model-space data to clip-space data.  To avoid
    // repeatedly computing the projection-view matrix for each geometric
    // object, the product is stored and maintained in this class.
    inline Matrix4x4<float> const& GetProjectionViewMatrix() const;

    // The preview matrix is applied after the model-to-world but before the
    // view matrix.  It is used for transformations such as reflections of
    // world objects.  The default value is the identity matrix.
    void SetPreViewMatrix(Matrix4x4<float> const& preViewMatrix);
    inline Matrix4x4<float> const& GetPreViewMatrix() const;
    inline bool PreViewIsIdentity() const;

    // The postprojection matrix is used for screen-space transformations such
    // as reflection of the rendered image.  The default value is the identity
    // matrix.
    void SetPostProjectionMatrix(Matrix4x4<float> const& postProjMatrix);
    inline Matrix4x4<float> const& GetPostProjectionMatrix() const;
    inline bool PostProjectionIsIdentity() const;

private:
    // Compute the view matrix after the frame changes.
    void OnFrameChange();

    // Compute the projection matrices after the frustum changes.
    void OnFrustumChange();

    // Compute the product postprojection-projection-view-preview.
    void UpdatePVMatrix();

    // The world coordinate frame.
    Vector4<float> mPosition, mDVector, mUVector, mRVector;

    // The view matrix for the camera.  The storage order depends on
    // whether you define GTE_USE_MAT_VEC or GTE_USE_VEC_MAT.
    Matrix4x4<float> mViewMatrix;

    // The projection matrices for the camera.  The storage order depends on
    // whether you define GTE_USE_MAT_VEC or GTE_USE_VEC_MAT.
    Matrix4x4<float> mProjectionMatrix;

    // The product of the projection and view matrix.  This includes the
    // post-projection and/or pre-view whenever those are not the identity
    // matrix.
    Matrix4x4<float> mProjectionViewMatrix;

    // The preview matrix for the camera.
    Matrix4x4<float> mPreViewMatrix;

    // The postprojection matrix for the camera.
    Matrix4x4<float> mPostProjectionMatrix;

    // The view frustum, stored in order as dmin (near), dmax (far),
    // umin (bottom), umax (top), rmin (left), and rmax (right).
    float mFrustum[VF_QUANTITY];

    // This member is 'true' for a perspective camera or 'false' for an
    // orthographic camera.
    bool mIsPerspective;

    // Indicates whether a user has specified a nonidentity pre-view matrix.
    bool mPreViewIsIdentity;

    // Indicates whether a user has specified a nonidentity post-projection
    // matrix.
    bool mPostProjectionIsIdentity;

    // The use of this is controlled by conditional compilation (via
    // GTE_VALIDATE_CAMERA_FRAME_ONCE).  It allows you to trap incorrectly
    // built camera frames or frames that are askew due to numerical
    // round-off errors.
    bool mValidateCameraFrame;
};

//----------------------------------------------------------------------------
inline Vector4<float> const& Camera::GetPosition() const
{
    return mPosition;
}
//----------------------------------------------------------------------------
inline Vector4<float> const& Camera::GetDVector() const
{
    return mDVector;
}
//----------------------------------------------------------------------------
inline Vector4<float> const& Camera::GetUVector() const
{
    return mUVector;
}
//----------------------------------------------------------------------------
inline Vector4<float> const& Camera::GetRVector() const
{
    return mRVector;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Camera::GetViewMatrix() const
{
    return mViewMatrix;
}
//----------------------------------------------------------------------------
inline bool Camera::IsPerspective() const
{
    return mIsPerspective;
}
//----------------------------------------------------------------------------
inline float const* Camera::GetFrustum() const
{
    return mFrustum;
}
//----------------------------------------------------------------------------
inline float Camera::GetDMin() const
{
    return mFrustum[VF_DMIN];
}
//----------------------------------------------------------------------------
inline float Camera::GetDMax() const
{
    return mFrustum[VF_DMAX];
}
//----------------------------------------------------------------------------
inline float Camera::GetUMin() const
{
    return mFrustum[VF_UMIN];
}
//----------------------------------------------------------------------------
inline float Camera::GetUMax() const
{
    return mFrustum[VF_UMAX];
}
//----------------------------------------------------------------------------
inline float Camera::GetRMin() const
{
    return mFrustum[VF_RMIN];
}
//----------------------------------------------------------------------------
inline float Camera::GetRMax() const
{
    return mFrustum[VF_RMAX];
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Camera::GetProjectionMatrix() const
{
    return mProjectionMatrix;
}
//----------------------------------------------------------------------------
inline void Camera::SetProjectionMatrix(Matrix4x4<float> const& projMatrix)
{
    mProjectionMatrix = projMatrix;
    UpdatePVMatrix();
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Camera::GetProjectionViewMatrix() const
{
    return mProjectionViewMatrix;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Camera::GetPreViewMatrix() const
{
    return mPreViewMatrix;
}
//----------------------------------------------------------------------------
inline bool Camera::PreViewIsIdentity() const
{
    return mPreViewIsIdentity;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Camera::GetPostProjectionMatrix() const
{
    return mPostProjectionMatrix;
}
//----------------------------------------------------------------------------
inline bool Camera::PostProjectionIsIdentity() const
{
    return mPostProjectionIsIdentity;
}
//----------------------------------------------------------------------------

}
