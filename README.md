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

![배포 아키텍처](./architecture.png)

- **Frontend 배포**: GitHub → GitHub Actions(CI Check) → 정적 빌드 결과물 S3 업로드 → CloudFront로 정적 자산 서빙
- **Backend 배포**: GitHub → GitHub Actions(CI Check, Docker 빌드) → ECR 이미지 푸시 → ArgoCD가 변경 감지 후 EKS 클러스터에 자동 배포(GitOps)
- **트래픽 흐름**: Route53 → CloudFront(정적 자산) / ALB(API 트래픽) → EKS Ingress → 각 Pod
- **EKS 클러스터 구성**: 하나의 노드 그룹 내에서 노드를 2개로 분리하여 역할 분담
  - Node 1 (AI Pod): ResNet-50, WatsonX 기반 AI 모델 서빙
  - Node 2 (Backend Pod): FastAPI 서버
- **DB 연결**: Backend Pod → SQL Query → AWS RDS(MySQL)

배포 과정 상세 정리는 아래 블로그 글 2편에 나눠서 기록했습니다.
- [배포 과정 정리 (1) - Docker/ECR/EKS 구성](https://myblog73329.tistory.com/101)
- [배포 과정 정리 (2) - ArgoCD/GitOps 배포 흐름](https://myblog73329.tistory.com/102)

## CI/CD 파이프라인

1. **CI (GitHub Actions)**: main 브랜치 push 시 Docker 이미지를 빌드하고 AWS ECR에 푸시
2. **CD (ArgoCD)**: ECR에 새 이미지가 올라오면 ArgoCD가 변경 사항을 감지해 EKS 클러스터에 자동 배포 (GitOps 방식)
3. **트래픽 라우팅**: ALB → Ingress를 통해 외부 도메인과 클러스터 내부 서비스 연결

## 사용한 AWS 서비스

- **EKS**: 백엔드 API, AI 모델 서빙 컨테이너를 운영하는 쿠버네티스 클러스터
- **RDS (MySQL)**: 서비스 데이터베이스
- **ALB**: API 트래픽 라우팅
- **VPC / NAT**: 네트워크 구성 및 프라이빗 서브넷의 외부 통신 처리

## 나의 기여 (이기준)

- Docker 이미지 빌드 및 AWS ECR 푸시 파이프라인 구축
- ArgoCD 기반 GitOps로 EKS 클러스터 자동 배포 구성
- ALB/Ingress를 통한 도메인 연결 및 API 트래픽 라우팅 설정
- EKS 클러스터 노드 그룹 구성 (백엔드/AI 모델 노드 분리)
- 백엔드-프론트엔드 최종 연동 및 통합 테스트, 연동 과정에서 발생한 코드 수정
- AI 파이프라인 연동, 또래 비교 분석을 위한 또래 데이터 수집

## 담당 역할 (Team)

| 팀원 | 담당 |
|---|---|
| 이기준 | AI 파이프라인 연동, 또래 데이터 수집, 배포/인프라(CI/CD, EKS, GitOps) |
| 강민구 | 아이 라벨 데이터 수집, LLM 에이전트 개발, 마일스톤 데이터 수집 |
| 윤기은 | 아이 라벨 데이터 수집 & 전처리, AI 모델 파인튜닝 |
| 이종훈 | 아이 라벨 데이터 수집 & 전처리, AI 모델 파인튜닝 |
| 권아림 | AI 모델 파인튜닝, TIP 데이터 수집 |
