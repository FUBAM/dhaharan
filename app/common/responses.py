from app.common.schemas import ApiResponse


def success_response(
    message: str,
    data=None
):
    return ApiResponse(
        success=True,
        message=message,
        data=data
    )


def error_response(
    message: str,
    data=None
):
    return ApiResponse(
        success=False,
        message=message,
        data=data
    )