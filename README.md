# 아이 성장 일기 AI - Backend & Infra

AI가 아이의 성장 과정을 분석·기록하여, 매년 생일마다 "디지털 성장 일기(북)"을 자동으로 생성해주는 육아 기록 서비스의 백엔드 및 배포 인프라 레포입니다.

> 원본 팀 프로젝트를 기반으로, 개인 포트폴리오 정리를 위해 별도 레포로 재구성했습니다.
> 원본 팀 프로젝트 레포: [IBM_RedHat_Final_Project_BE](https://github.com/Leegijun11/IBM_RedHat_Final_Project_BE)

## 서비스 개요

아이의 성장 과정을 AI가 분석·기록하여, 생일을 기준으로 "디지털 성장 일기(북)"을 자동 생성해주는 육아 기록 서비스입니다. (핵심 기능은 [프론트엔드 레포](https://github.com/Leegijun11/growbook-ai) 참고)

## 기술 스택

| 영역 | 기술 |
|---|---|
| 백엔드 | FastAPI, SQLAlchemy, Starlette |
| AI | PyTorch, torchvision, langchain-openai 0.2.5 |
| 데이터베이스 | MySQL (AWS RDS) |
| 인프라 | AWS EKS, ALB, CloudFront, S3, VPC, NAT |
| CI/CD | Docker, GitHub Actions (CI), ArgoCD (CD, GitOps) |

## 배포 아키텍처

![배포 아키텍처](./architecture.PNG)

- **Frontend 배포**: GitHub → GitHub Actions(CI Check) → 정적 빌드 결과물 S3 업로드 → CloudFront로 정적 자산 서빙
- **Backend 배포**: GitHub → GitHub Actions(CI Check, Docker 빌드) → ECR 이미지 푸시 → ArgoCD가 변경 감지 후 EKS 클러스터에 자동 배포(GitOps)
- **트래픽 흐름**: Route53 → CloudFront(정적 자산) / ALB(API 트래픽) → EKS Ingress → 각 Pod
- **DB 연결**: Backend Pod → SQL Query → AWS RDS(MySQL)

배포 과정 상세 정리는 아래 블로그 글 2편에 나눠서 기록했습니다.
- [배포 과정 정리 (1) - Docker/ECR/EKS 구성](https://myblog73329.tistory.com/101)
- [배포 과정 정리 (2) - ArgoCD/GitOps 배포 흐름](https://myblog73329.tistory.com/102)

## CI/CD 파이프라인

1. **CI (GitHub Actions)**: main 브랜치 push 시 Docker 이미지를 빌드해 AWS ECR에 푸시하고, 같은 워크플로가 `k8s/deployment.yaml`의 이미지 태그(커밋 해시)를 새 버전으로 바꿔 Git에 커밋
2. **CD (ArgoCD)**: ArgoCD가 Git의 배포 파일 변경을 감지해 EKS 클러스터에 자동 배포 (GitOps 방식)
3. **트래픽 라우팅**: ALB → Ingress를 통해 외부 도메인(HTTPS)과 클러스터 내부 서비스 연결, `/health`로 헬스체크

## 사용한 AWS 서비스

- **EKS**: 백엔드 API 컨테이너를 운영하는 쿠버네티스 클러스터
- **RDS (MySQL)**: 서비스 데이터베이스
- **ALB**: API 트래픽 라우팅
- **VPC / NAT**: 네트워크 구성 및 프라이빗 서브넷의 외부 통신 처리

## 나의 기여 (이기준)

이 프로젝트에서 저는 조장으로서 **개발보다는 기획과 점검** 쪽을 맡았습니다.

- GitHub Actions로 Docker 이미지 빌드 → AWS ECR 푸시 → 배포 파일의 이미지 태그 갱신 → ArgoCD(GitOps)로 EKS 배포까지 이어지는 **CI/CD 파이프라인 구성**
- 이 프로젝트의 **배포 아키텍처 전체 흐름 정리** (프론트: S3·CloudFront, 백엔드: ECR·ArgoCD·EKS·ALB Ingress)
- 백엔드-프론트엔드 최종 연동 및 통합 점검: 서버가 요구하는 요청 값의 구조와 프론트가 넘기는 값이 맞지 않는 경우, 수정본을 합친 뒤 원래 되던 API가 깨진 경우 등을 확인하고 코드를 수정 (점검은 수동으로 진행)
- 또래 비교 분석을 위한 또래 데이터 수집

> **참고**: Docker와 쿠버네티스는 이 프로젝트에서 **완전히 이해한 상태로 다뤘다기보다 처음 접해 본 수준**입니다. 배포 아키텍처를 CI/CD까지 전체적으로 설명할 수 있는 정도이고, 클러스터 내부 설계(노드 구성, 네트워크 등)를 깊이 다루지는 않았습니다.

## 담당 역할 (Team)

| 팀원 | 담당 |
|---|---|
| 이기준 (조장) | 기획, 백엔드-프론트엔드 연동 점검, 또래 데이터 수집, 배포 파이프라인(CI/CD) |
| 강민구 | 아이 라벨 데이터 수집, LLM 에이전트 개발, 마일스톤 데이터 수집 |
| 윤기은 | 아이 라벨 데이터 수집 & 전처리, AI 모델 파인튜닝 |
| 이종훈 | 아이 라벨 데이터 수집 & 전처리, AI 모델 파인튜닝 |
| 권아림 | AI 모델 파인튜닝, TIP 데이터 수집 |
