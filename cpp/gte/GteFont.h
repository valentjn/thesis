// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/12/13)

#pragma once

#include <gte/GteIndexBuffer.h>
#include <gte/GteTextEffect.h>
#include <gte/GteVertexBuffer.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Font
{
public:
    // Construction.
    Font(unsigned int width, unsigned int height, char const* texels,
        float const* characterData, unsigned int maxMessageLength);

    // Member access.
    inline std::shared_ptr<VertexBuffer> const& GetVertexBuffer() const;
    inline std::shared_ptr<IndexBuffer> const& GetIndexBuffer() const;
    inline std::shared_ptr<TextEffect> const& GetTextEffect() const;

    // Populate the vertex buffer for the specified string.
    void Typeset(int viewportWidth, int viewportHeight, int x, int y,
        Vector4<float> const& color, std::string const& message) const;

    // Naming support, used in the DX11 debug layer.  The default name is "".
    // If you want the name to show up in the DX11 destruction messages when
    // the associated DX11GraphicsObject is destroyed, set the name to
    // something other than "".
    void SetName(std::string const& name);
    inline std::string const& GetName() const;

protected:
    std::string mName;
    unsigned int mMaxMessageLength;
    std::shared_ptr<VertexBuffer> mVertexBuffer;
    std::shared_ptr<IndexBuffer> mIndexBuffer;
    std::shared_ptr<Texture2> mTexture;
    std::shared_ptr<TextEffect> mTextEffect;
    float mCharacterData[257];
    static std::string Font::msHLSLString;
};

//----------------------------------------------------------------------------
inline std::shared_ptr<VertexBuffer> const& Font::GetVertexBuffer() const
{
    return mVertexBuffer;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<IndexBuffer> const& Font::GetIndexBuffer() const
{
    return mIndexBuffer;
}
//----------------------------------------------------------------------------
inline std::shared_ptr<TextEffect> const& Font::GetTextEffect() const
{
    return mTextEffect;
}
//----------------------------------------------------------------------------
inline std::string const& Font::GetName() const
{
    return mName;
}
//----------------------------------------------------------------------------

}
