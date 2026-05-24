rootProject.name = "github-actions"

include("skeletons:spring", "skeletons:ktor")

project(":skeletons:spring").projectDir = file("skeletons/spring")
project(":skeletons:ktor").projectDir = file("skeletons/ktor")
