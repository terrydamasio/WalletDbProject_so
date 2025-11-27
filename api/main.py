from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.routers.carteira_router import router as carteiras_router
from api.routers.deposito_saque_router import router as deposito_saque_router
from api.routers.conversao_router import router as conversao_router
from api.routers.transferencia_router import router as transferencia_router


def create_app() -> FastAPI:
    
    app = FastAPI(
        title="Carteira Digital API",
        version="1.0.0",
        description="API educacional de carteira digital com SQL puro e FastAPI.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/", tags=["Health Check"])
    def root():
        """
        Endpoint raiz para verificar se a API está rodando.
        """
        return JSONResponse(
            content={
                "message": "🚀 Carteira Digital API está rodando!",
                "version": "1.0.0",
                "status": "online",
                "docs": "/docs",
            },
            status_code=200,
        )

    @app.get("/health", tags=["Health Check"])
    def health_check():
        """
        Endpoint de health check para monitoramento.
        """
        from api.persistence.db import test_connection
        
        db_status = "✅ Conectado" if test_connection() else "❌ Falha"
        
        return JSONResponse(
            content={
                "api": "online",
                "database": db_status,
            },
            status_code=200,
        )

    # ========================================
    # REGISTRAR ROUTERS (será feito nas próximas sprints)
    # ========================================
    
    app.include_router(carteiras_router)
    app.include_router(deposito_saque_router)
    app.include_router(conversao_router)
    app.include_router(transferencia_router)

    app.include_router(carteiras_router)

    return app


# ========================================
# INSTÂNCIA DA APLICAÇÃO
# ========================================

app = create_app()


# ========================================
# EXECUÇÃO DIRETA (opcional)
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload em desenvolvimento
    )
