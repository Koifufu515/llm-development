{{- define "wenshu.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "wenshu.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
{{- end -}}

{{- define "wenshu.env" -}}
- name: STORAGE_MODE
  value: "mongo"
- name: VECTOR_BACKEND
  value: {{ .Values.model.vectorBackend | quote }}
- name: EMBEDDING_PROVIDER
  value: {{ .Values.model.embeddingProvider | quote }}
- name: EMBEDDING_MODEL
  value: {{ .Values.model.embeddingModel | quote }}
- name: DEEPSEEK_MODEL
  value: {{ .Values.model.deepseekModel | quote }}
- name: DEEPSEEK_BASE_URL
  value: {{ .Values.model.deepseekBaseUrl | quote }}
- name: RELAY_BASE_URL
  value: {{ .Values.model.relayBaseUrl | quote }}
- name: DEEPSEEK_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: DEEPSEEK_API_KEY
- name: RELAY_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: RELAY_API_KEY
- name: MONGODB_URI
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: MONGODB_URI
- name: REDIS_ADDR
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: REDIS_ADDR
- name: AUTH_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: AUTH_SECRET
- name: INTERNAL_API_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ include "wenshu.fullname" . }}-secret
      key: INTERNAL_API_TOKEN
- name: SEED_DEMO_USERS
  value: "false"
- name: PI_AGENT_ENABLED
  value: "true"
- name: PI_AGENT_URL
  value: "http://pi-agent:8100"
- name: MONGODB_DB
  value: {{ .Values.model.database | quote }}
- name: EMBEDDING_DIM
  value: {{ .Values.model.embeddingDim | quote }}
- name: MILVUS_URI
  value: {{ .Values.model.milvusUri | quote }}
- name: MILVUS_COLLECTION
  value: {{ .Values.model.milvusCollection | quote }}
- name: RERANKER_MODEL
  value: {{ .Values.model.rerankerModel | quote }}
- name: RERANKER_URL
  value: {{ .Values.model.rerankerUrl | quote }}
- name: REDIS_SENTINEL_HOSTS
  value: {{ .Values.redisSentinel.hosts | quote }}
- name: REDIS_SENTINEL_SERVICE
  value: {{ .Values.redisSentinel.service | quote }}
- name: PRIVACY_REDACTION_FILE
  value: /run/privacy/privacy-map.json
- name: OTEL_ENABLED
  value: "true"
- name: OTEL_ENDPOINT
  value: "http://otel-collector:4318"
- name: MODEL_EGRESS_ALLOWED
  value: "true"

{{- end -}}


{{- define "wenshu.privacyMount" -}}
{{- if .Values.privacy.enabled }}
- name: privacy
  mountPath: /run/privacy
  readOnly: true
{{- end }}
{{- end -}}
{{- define "wenshu.privacyVolume" -}}
{{- if .Values.privacy.enabled }}
- name: privacy
  secret:
    secretName: {{ .Values.privacy.secretName }}
{{- end }}
{{- end -}}
