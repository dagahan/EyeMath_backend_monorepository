variable "REGISTRY" { default = "ghcr.io/your-org" }
variable "PROJECT"  { default = "eye-math" }
variable "VERSION"  { default = "0.1.0" }
variable "SHA"      { default = "dev" }

variable "PLATFORMS" { default = ["linux/amd64","linux/arm64"] }

group "dev"     { targets = ["nginx","gateway","authorizer","recognizer","renderer","valkey","postgres"] }
group "release" { targets = ["nginx","gateway","authorizer","recognizer","renderer","valkey","postgres"] }


target "common" {
  platforms   = var.PLATFORMS
  pull        = true
  cache-to    = ["type=registry,ref=${REGISTRY}/${PROJECT}/buildcache:all,mode=max"]
  cache-from  = ["type=registry,ref=${REGISTRY}/${PROJECT}/buildcache:all"]
}


target "nginx" {
  inherits   = ["common"]
  context    = "./nginx"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/nginx:${VERSION}", "${REGISTRY}/${PROJECT}/nginx:${SHA}"]
}


target "gateway" {
  inherits   = ["common"]
  context    = "./gateway"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/gateway:${VERSION}", "${REGISTRY}/${PROJECT}/gateway:${SHA}"]
}


target "authorizer" {
  inherits   = ["common"]
  context    = "./authorizer"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/authorizer:${VERSION}", "${REGISTRY}/${PROJECT}/authorizer:${SHA}"]
}


target "recognizer" {
  inherits   = ["common"]
  context    = "./recognizer"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/recognizer:${VERSION}", "${REGISTRY}/${PROJECT}/recognizer:${SHA}"]
}


target "renderer" {
  inherits   = ["common"]
  context    = "./renderer"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/renderer:${VERSION}", "${REGISTRY}/${PROJECT}/renderer:${SHA}"]
}


target "valkey" {
  inherits   = ["common"]
  context    = "./valkey"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/valkey:${VERSION}", "${REGISTRY}/${PROJECT}/valkey:${SHA}"]
}


target "postgres" {
  inherits   = ["common"]
  context    = "./postgres"
  dockerfile = "dockerfile"
  tags       = ["${REGISTRY}/${PROJECT}/postgres:${VERSION}", "${REGISTRY}/${PROJECT}/postgres:${SHA}"]
}


