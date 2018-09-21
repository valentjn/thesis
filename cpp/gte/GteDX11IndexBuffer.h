// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteDX11Buffer.h>
#include <gte/GteIndexBuffer.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP DX11IndexBuffer : public DX11Buffer
{
public:
    // Construction and destruction.
    virtual ~DX11IndexBuffer();
    DX11IndexBuffer(ID3D11Device* device, IndexBuffer const* vbuffer);
    static DX11GraphicsObject* Create(ID3D11Device* device,
        GraphicsObject const* object);

    // Member access.
    IndexBuffer* GetIndexBuffer() const;

    // Drawing support.
    void Enable(ID3D11DeviceContext* context);
    void Disable(ID3D11DeviceContext* context);

private:
    DXGI_FORMAT mFormat;
};

}
