// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/12/13)

#pragma once

#include <gte/GteIndexBuffer.h>
#include <gte/GteSamplerState.h>
#include <gte/GteTexture2.h>
#include <gte/GteVector2.h>
#include <gte/GteVertexBuffer.h>
#include <gte/GteVisualEffect.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP OverlayEffect
{
public:
    // Create an overlay that allows you to use a simple color shader or a
    // simple gray-scale shader.
    OverlayEffect(int windowWidth, int windowHeight, int textureWidth,
        int textureHeight, SamplerState::Filter filter,
        SamplerState::Mode mode0, SamplerState::Mode mode1,
        bool useColorPShader);

    // Create an overlay that uses a pixel shader other than the color or
    // gray default shaders.
    OverlayEffect(int windowWidth, int windowHeight, int textureWidth,
        int textureHeight, std::shared_ptr<PixelShader> const& pixelShader);

    // Access to the overlay rectangle (px,py,pw,ph), which is in client
    // window coordinates.  The upper-right corner of the overlay rectangle
    // is (px,py).  The width and height of the rectangle are pw and ph,
    // respectively.  The width and height must be positive.  The corner
    // (px,py) may be chosen outside the client window, allowing you to clip
    // overlays against the window boundaries.
    inline void SetOverlayRectangle(std::array<int,4> const& rectangle);
    inline std::array<int,4> GetOverlayRectangle() const;

    // Access to the texture rectangle (tx,ty,tw,th), which is in texture
    // image coordinates.  The upper-right corner of the texture rectangle
    // is (tx,ty).  The width and height of the rectangle are tw and th,
    // respectively.  The width and height must be positive.  The corner
    // (tx,ty) may be chosen outside the texture image, but be aware that the
    // colors drawn outside will depend on the sampler state mode.
    void SetTextureRectangle(std::array<int,4> const& rectangle);
    inline std::array<int,4> GetTextureRectangle() const;

    // Joint setting of rectangles (rare case), allowing for a single vertex
    // buffer update.
    void SetRectangles(std::array<int,4> const& overlayRectangle,
        std::array<int,4> const& textureRectangle);

    // Test whether the input (x,y) is contained by the overlay rectangle.
    // This is useful for hit testing in user interfaces.
    bool Contains(int x, int y) const;

    // For DX11Engine::Draw(VertexBuffer*,IndexBuffer*,VisualEffect*).  The
    // vertex buffer is also needed for CPU-to-GPU copies when the overlay
    // and/or texture rectangles are modified.
    inline std::shared_ptr<VertexBuffer> const& GetVertexBuffer() const;
    inline std::shared_ptr<IndexBuffer> const& GetIndexBuffer() const;
    inline std::shared_ptr<VisualEffect> const& GetEffect() const;

    // Dynamically update the overlay textures.  The first function uses
    // the default name "imageTexture".  The second function allows you
    // to set textures when you create an overlay with your own pixel
    // shader.
    void SetTexture(std::shared_ptr<Texture2> const& texture);
    void SetTexture(std::string const& textureName,
        std::shared_ptr<Texture2> const& texture);

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    void SetName(std::string const& name);
    inline std::string const& GetName() const;

protected:
    void Initialize(int windowWidth, int windowHeight, int textureWidth,
        int textureHeight);

    struct Vertex
    {
        Vector2<float> position;
        Vector2<float> tcoord;
    };

    void UpdateVertexBuffer();

    std::string mName;
    float mWindowWidth, mWindowHeight;
    float mInvTextureWidth, mInvTextureHeight;
    std::array<int,4> mOverlayRectangle;
    std::array<int,4> mTextureRectangle;
    std::shared_ptr<VertexBuffer> mVBuffer;
    std::shared_ptr<IndexBuffer> mIBuffer;
    std::shared_ptr<VertexShader> mVShader;
    std::shared_ptr<PixelShader> mPShader;
    std::shared_ptr<VisualEffect> mEffect;

    static std::string const msVShaderString;
    static std::string const msColorPShaderString;
    static std::string const msGrayPShaderString;
};

//----------------------------------------------------------------------------
inline void OverlayEffect::SetOverlayRectangle(
    std::array<int, 4> const& rectangle)
{
    mOverlayRectangle = rectangle;
    UpdateVertexBuffer();
}
//----------------------------------------------------------------------------
inline std::array<int, 4> OverlayEffect::GetOverlayRectangle() const
{
    return mOverlayRectangle;
}
//----------------------------------------------------------------------------
inline std::array<int, 4> OverlayEffect::GetTextureRectangle() const
{
    return mTextureRectangle;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<VertexBuffer> const&
OverlayEffect::GetVertexBuffer() const
{
    return mVBuffer;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<IndexBuffer> const&
OverlayEffect::GetIndexBuffer() const
{
    return mIBuffer;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<VisualEffect> const&
OverlayEffect::GetEffect() const
{
    return mEffect;
}
//----------------------------------------------------------------------------
inline std::string const& OverlayEffect::GetName() const
{
    return mName;
}
//----------------------------------------------------------------------------

}
