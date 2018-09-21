// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteDX11TextureArray.h>
#include <gte/GteTextureCube.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP DX11TextureCube : public DX11TextureArray
{
public:
    // Construction and destruction.
    virtual ~DX11TextureCube();
    DX11TextureCube(ID3D11Device* device, TextureCube const* textureCube);
    static DX11GraphicsObject* Create(ID3D11Device* device,
        GraphicsObject const* object);

    // Member access.
    TextureCube* GetTexture() const;
    ID3D11Texture2D* GetDXTexture() const;

private:
    // Support for construction.
    void CreateStaging(ID3D11Device* device, D3D11_TEXTURE2D_DESC const& tx);
    void CreateSRView(ID3D11Device* device, D3D11_TEXTURE2D_DESC const& tx);
    void CreateUAView(ID3D11Device* device, D3D11_TEXTURE2D_DESC const& tx);
};

}
