// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.3 (2014/12/13)

#pragma once

#include <gte/GteCamera.h>
#include <gte/GteDX11Engine.h>
#include <gte/GteNode.h>
#include <gte/GteTimer.h>
#include <gte/GteTransform.h>
#include <gte/GteVisual.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Window
{
public:
    // All parameters for constructing windows are in this structure.  Derived
    // classes may define nested classes to derive from this.  The creation by
    // WindowSystem requires you to pass such a structure.
    struct GTE_IMPEXP Parameters
    {
        Parameters()
            :
            title(L""),
            xOrigin(0), yOrigin(0), xSize(0), ySize(0),
            allowResize(false), hscrollBar(false), vscrollBar(false),
            created(false),
            deviceCreationFlags(0),
            featureLevel(D3D_FEATURE_LEVEL_11_0),
            handle(nullptr),
            engine(nullptr)
        {
        }

        std::wstring title;
        int xOrigin, yOrigin, xSize, ySize;
        bool allowResize, hscrollBar, vscrollBar, created;
        UINT deviceCreationFlags;
        D3D_FEATURE_LEVEL featureLevel;
        HWND handle;
        DX11Engine* engine;
    };

protected:
    // Abstract base class.  Only WindowSystem may create windows.
    Window(Parameters& parameters);
public:
    virtual ~Window();

    // Member access.
    inline HWND GetHandle() const;
    inline void SetTitle(std::wstring const& title);
    inline std::wstring GetTitle() const;
    inline int GetXOrigin() const;
    inline int GetYOrigin() const;
    inline int GetXSize() const;
    inline int GetYSize() const;
    inline bool IsMinimized() const;
    inline bool IsMaximized() const;
    inline float GetAspectRatio() const;

    // Display callbacks.
    virtual void OnMove(int x, int y);
    virtual bool OnResize(int xSize, int ySize);
    virtual void OnMinimize();
    virtual void OnMaximize();
    virtual void OnDisplay();
    virtual void OnIdle();

    // Keyboard callbacks.  OnCharPress allows you to distinguish between
    // upper-case and lower-case letters; OnKeyDown and OnKeyUp do not.
    virtual bool OnCharPress(unsigned char key, int x, int y);
    virtual bool OnKeyDown(int key, int x, int y);
    virtual bool OnKeyUp(int key, int x, int y);

    // Mouse callbacks and state information.
    enum GTE_IMPEXP MouseButton
    {
        MOUSE_NONE,
        MOUSE_LEFT,
        MOUSE_MIDDLE,
        MOUSE_RIGHT
    };

    enum GTE_IMPEXP MouseState
    {
        MOUSE_UP,
        MOUSE_DOWN
    };

    virtual bool OnMouseClick(MouseButton button, MouseState state,
        int x, int y, unsigned int modifiers);

    virtual bool OnMouseMotion(MouseButton button, int x, int y,
        unsigned int modifiers);

    // The MSDN documentation for WM_MOUSEWHEEL states that the 'delta'
    // stored in the high-order word of wParam is the distance the wheel is
    // rotated, in multiples of WHEEL_DELTA.  This constant is 120.  Later in
    // the documentation, presumably something added later, there is mention
    // that finer-resolution wheels might report 'delta' smaller than 120.
    // The previous version of OnMouseWheel passed 'delta' but divided by
    // WHEEL_DELTA; for finer-resolution wheels, the input 'delta' to
    // OnMouseWheel was typically 0.  Now the input is simply the number
    // reported in wParam.
    virtual bool OnMouseWheel(int delta, int x, int y,
        unsigned int modifiers);

    void SetMousePosition(int x, int y);
    void GetMousePosition(int& x, int& y) const;

    // Scroll support.  The 'bar' value is 0 for horizontal scroll bars or 1
    // for vertical scroll bars.
    void SetScrollInterval(int bar, int minValue, int maxValue);
    void GetScrollInterval(int bar, int& minValue, int& maxValue) const;
    int SetScrollPosition(int bar, int value);
    int GetScrollPosition(int bar) const;

    // The return value of the increment/decrement functions is the delta of
    // the slider thumb.  If zero, the scroll state did not change.  For the
    // tracking functions, the return value is the current slider thumb
    // position.  A derived-class override must call the base-class function
    // first.
    virtual int OnScrollIncrementLoRes(int bar);
    virtual int OnScrollDecrementLoRes(int bar);
    virtual int OnScrollIncrementHiRes(int bar);
    virtual int OnScrollDecrementHiRes(int bar);
    virtual int OnScrollTracking(int bar);
    virtual int OnScrollEndTracking(int bar);

    // Performance measurements.
    inline void ResetTime();
    void MeasureTime();
    inline void UpdateFrameCount();

    // Draw the current frame rate at window location (x,y) using the
    // specified color.
    void DrawFrameRate(unsigned int x, unsigned int y,
        Vector4<float> const& color);

    // Camera motion using key strokes.
    void EnableCameraMotion(float trnSpeed, float rotSpeed,
        float trnSpeedFactor, float rotSpeedFactor);
    inline void DisableCameraMotion();
    virtual bool MoveCamera();
    virtual void MoveForward();
    virtual void MoveBackward();
    virtual void MoveUp();
    virtual void MoveDown();
    virtual void MoveRight();
    virtual void MoveLeft();
    virtual void TurnRight();
    virtual void TurnLeft();
    virtual void LookUp();
    virtual void LookDown();

    // Update the constant buffer's projection-view-world matrix (pvw-matrix)
    // when the camera's view or projection matrices change.  The input
    // 'pvwMatrixName' is the name specified in the shader program and is
    // used in calls to ConstantBuffer::SetMember<Matrix4x4<float>>(...).
    // The update is automatic during calls to Resize(int,int) or 
    // MoveCamera(), using internal calls to UpdatePVWMatrices().  If you
    // modify the view or projection matrices directly through the Camera
    // interface, you are responsible for calling UpdatePVWMatrices().
    // The address of 'worldMatrix' is used as a key to a std::map, so be
    // careful to ensure that 'worldMatrix' persists until a call to
    // Unsubscribe.  The return value of Subscribe(...) is 'true' as long
    // as 'cbuffer' is not already subscribed and actually has a member named
    // 'pvwMatrixName'.  The return value of Unsubscribe(...) is true if and
    // only if the input matrix is currently subscribed.
    bool Subscribe(Matrix4x4<float> const& worldMatrix,
        std::shared_ptr<ConstantBuffer> const& cbuffer,
        std::string const& pvwMatrixName = "pvwMatrix");
    bool Unsubscribe(Matrix4x4<float> const& worldMatrix);
    void UpdatePVWMatrices();

    // Object rotation using a virtual trackball.
    inline void EnableObjectMotion();
    inline void DisableObjectMotion();
    inline Matrix4x4<float> const& GetTrackballRotation() const;

    // Update the object's world matrix using post-multiplication by the
    // virtual trackball's rotation.  This is accomplished by attaching
    // the subscribed objects as children of a node whose world transform
    // is the trackball rotation.  The Subscribe(...) function returns
    // 'true' as long as 'object' is not already subscribed, is not null,
    // and has no parent.  The Unsubscribe(...) function returns 'true' as
    // long as 'object' is currently subscribed.
    bool Subscribe(std::shared_ptr<Spatial> const& object);
    bool Unsubscribe(std::shared_ptr<Spatial> const& object);
    void UpdateWMatrices();

    // Subscribe for both camera and world transform changes.  The world
    // matrix of the 'visual' object is used to subscribe to camera changes.
    bool SubscribeCW(std::shared_ptr<Visual> const& visual,
        std::shared_ptr<ConstantBuffer> const& cbuffer,
        std::string const& pvwMatrixName = "pvwMatrix");
    bool UnsubscribeCW(std::shared_ptr<Visual> const& visual);
    void UpdateCW();

    // Compute a picking line from the left-handed screen coordinates (x,y),
    // the viewport, and the camera.  The output 'origin' is the camera
    // position and the 'direction' is a unit-length vector, both in world
    // coordinates.  The return value is 'true' iff (x,y) is in the viewport.
    bool GetPickLine(int x, int y, Vector4<float>& origin,
        Vector4<float>& direction);

protected:
    void RotateTrackBall(float x0, float y0, float x1, float y1);

    // Standard window information.
    HWND mHandle;
    std::wstring mTitle;
    int mXOrigin, mYOrigin, mXSize, mYSize;
    bool mAllowResize;
    bool mIsMinimized;
    bool mIsMaximized;

    // Scroll bar support.
    bool mHasScroll[2];
    mutable SCROLLINFO mScrollInfo[2];
    int mScrollLoResDelta[2];
    int mScrollHiResDelta[2];

    // Performance measurement parameters.
    double mLastTime, mAccumulatedTime, mFrameRate;
    int mFrameCount, mAccumulatedFrameCount, mTimer, mMaxTimer;
    Timer mClock;

    // Graphics device and camera.
    DX11Engine* mEngine;
    Camera mCamera;

    // Camera motion support.
    Vector4<float> mWorldAxis[3];
    float mTrnSpeed, mTrnSpeedFactor;
    float mRotSpeed, mRotSpeedFactor;
    bool mUpArrowPressed;
    bool mDownArrowPressed;
    bool mLeftArrowPressed;
    bool mRightArrowPressed;
    bool mPageUpPressed;
    bool mPageDownPressed;
    bool mHomePressed;
    bool mEndPressed;
    bool mInsertPressed;
    bool mDeletePressed;
    bool mCameraMovable;

    // Subscribers to camera matrix changes.
    typedef Matrix4x4<float> const* PVWKey;
    typedef std::pair<std::shared_ptr<ConstantBuffer>, std::string> PVWValue;
    std::map<PVWKey, PVWValue> mCameraSubscribers;

    // Object motion support using a virtual trackball.
    std::shared_ptr<Node> mTrackballNode;
    float mXTrack0, mYTrack0, mXTrack1, mYTrack1;
    Matrix4x4<float> mSaveRotate;
    bool mUseTrackball, mTrackballDown;
};

//----------------------------------------------------------------------------
inline HWND Window::GetHandle() const
{
    return mHandle;
}
//----------------------------------------------------------------------------
inline std::wstring Window::GetTitle() const
{
    return mTitle;
}
//----------------------------------------------------------------------------
inline int Window::GetXOrigin() const
{
    return mXOrigin;
}
//----------------------------------------------------------------------------
inline int Window::GetYOrigin() const
{
    return mYOrigin;
}
//----------------------------------------------------------------------------
inline int Window::GetXSize() const
{
    return mXSize;
}
//----------------------------------------------------------------------------
inline int Window::GetYSize() const
{
    return mYSize;
}
//----------------------------------------------------------------------------
inline bool Window::IsMinimized() const
{
    return mIsMinimized;
}
//----------------------------------------------------------------------------
inline bool Window::IsMaximized() const
{
    return mIsMaximized;
}
//----------------------------------------------------------------------------
inline float Window::GetAspectRatio() const
{
    return (float)mXSize / (float)mYSize;
}
//----------------------------------------------------------------------------
inline void Window::ResetTime()
{
    mLastTime = -1.0;
}
//----------------------------------------------------------------------------
inline void Window::UpdateFrameCount()
{
    ++mFrameCount;
}
//----------------------------------------------------------------------------
inline void Window::DisableCameraMotion()
{
    mCameraMovable = false;
}
//----------------------------------------------------------------------------
inline void Window::EnableObjectMotion()
{
    mUseTrackball = true;
}
//----------------------------------------------------------------------------
inline void Window::DisableObjectMotion()
{
    mUseTrackball = false;
}
//----------------------------------------------------------------------------
inline Matrix4x4<float> const& Window::GetTrackballRotation() const
{
    return mTrackballNode->worldTransform;
}
//----------------------------------------------------------------------------

}
