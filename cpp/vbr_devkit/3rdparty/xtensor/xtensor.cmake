include(FetchContent)
FetchContent_Declare(xtl
        GIT_REPOSITORY https://github.com/xtensor-stack/xtl.git
        GIT_TAG d11fb6b5f4c417025124ed2c62175284846a1914

)
FetchContent_Declare(xtensor
        GIT_REPOSITORY https://github.com/xtensor-stack/xtensor.git
        GIT_TAG d9c3782ed51027b2d00be3c26288b2f74e4dbe94
)
FetchContent_MakeAvailable(xtl xtensor)
