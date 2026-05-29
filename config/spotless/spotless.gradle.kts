initscript {
    repositories {
        gradlePluginPortal()
    }

    dependencies {
        classpath("com.diffplug.spotless:spotless-plugin-gradle:8.6.0")
    }
}

allprojects {
    pluginManager.withPlugin("org.jetbrains.kotlin.jvm") {
        plugins.apply(com.diffplug.gradle.spotless.SpotlessPlugin::class.java)

        extensions.configure<com.diffplug.gradle.spotless.SpotlessExtension>("spotless") {
            kotlin {
                target("**/*.kt")
                ktlint()
            }

            kotlinGradle {
                target("**/*.gradle.kts")
                ktlint()
            }
        }
    }
}
