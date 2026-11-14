import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val appVersion = (project.findProperty("appVersion") as String).toInt()

// One key for the life of the app, so every build installs over the last one. The key is not in the
// repository (it is public since 14.11.2026): the workflow writes signing/test-builds.p12 from the secret
// SIGNING_KEYSTORE_B64 and passes SIGNING_STORE_PASSWORD and SIGNING_KEY_ALIAS. On the Mac they stay local in signing/
// (gitignored): test-builds.p12 and signing.properties (storePassword=..., keyAlias=...).
val keystoreFile = rootProject.file("signing/test-builds.p12")
val signingProps = Properties().apply {
    val f = rootProject.file("signing/signing.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}
val storePass: String = System.getenv("SIGNING_STORE_PASSWORD") ?: signingProps.getProperty("storePassword", "")
val keyAliasName: String = System.getenv("SIGNING_KEY_ALIAS") ?: signingProps.getProperty("keyAlias", "")

android {
    namespace = "com.mantraproductions.sonyremote"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.mantraproductions.sonyremote"
        minSdk = 29
        targetSdk = 35
        versionCode = appVersion
        versionName = appVersion.toString()
        // 64-bit ARM only: every phone of the last years; keeps the APK under Cloudflare Pages' 25 MB (29.10.2026)
        ndk { abiFilters += listOf("arm64-v8a") }
    }

    signingConfigs {
        create("testBuilds") {
            storeFile = keystoreFile
            storePassword = storePass
            keyAlias = keyAliasName
            keyPassword = storePass
            storeType = "PKCS12"
        }
    }

    buildTypes {
        debug {
            signingConfig = signingConfigs.getByName("testBuilds")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    // TC JAM: reading a camera's time code from its screen, on the phone, offline (29.10.2026)
    implementation("com.google.mlkit:text-recognition:16.0.1")
    testImplementation("junit:junit:4.13.2")
}
