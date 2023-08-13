/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { AuthService } from './services/AuthService';
import { BigPlanService } from './services/BigPlanService';
import { ChoreService } from './services/ChoreService';
import { DefaultService } from './services/DefaultService';
import { EmailTaskService } from './services/EmailTaskService';
import { GcService } from './services/GcService';
import { GenService } from './services/GenService';
import { GetSummariesService } from './services/GetSummariesService';
import { HabitService } from './services/HabitService';
import { InboxTaskService } from './services/InboxTaskService';
import { InitService } from './services/InitService';
import { LoadProgressReporterTokenService } from './services/LoadProgressReporterTokenService';
import { LoadTopLevelInfoService } from './services/LoadTopLevelInfoService';
import { LoginService } from './services/LoginService';
import { MetricService } from './services/MetricService';
import { PersonService } from './services/PersonService';
import { ProjectService } from './services/ProjectService';
import { ReportService } from './services/ReportService';
import { SearchService } from './services/SearchService';
import { SlackTaskService } from './services/SlackTaskService';
import { SmartListService } from './services/SmartListService';
import { UserService } from './services/UserService';
import { VacationService } from './services/VacationService';
import { WorkspaceService } from './services/WorkspaceService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class ApiClient {

    public readonly auth: AuthService;
    public readonly bigPlan: BigPlanService;
    public readonly chore: ChoreService;
    public readonly default: DefaultService;
    public readonly emailTask: EmailTaskService;
    public readonly gc: GcService;
    public readonly gen: GenService;
    public readonly getSummaries: GetSummariesService;
    public readonly habit: HabitService;
    public readonly inboxTask: InboxTaskService;
    public readonly init: InitService;
    public readonly loadProgressReporterToken: LoadProgressReporterTokenService;
    public readonly loadTopLevelInfo: LoadTopLevelInfoService;
    public readonly login: LoginService;
    public readonly metric: MetricService;
    public readonly person: PersonService;
    public readonly project: ProjectService;
    public readonly report: ReportService;
    public readonly search: SearchService;
    public readonly slackTask: SlackTaskService;
    public readonly smartList: SmartListService;
    public readonly user: UserService;
    public readonly vacation: VacationService;
    public readonly workspace: WorkspaceService;

    public readonly request: BaseHttpRequest;

    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '0.1.0',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });

        this.auth = new AuthService(this.request);
        this.bigPlan = new BigPlanService(this.request);
        this.chore = new ChoreService(this.request);
        this.default = new DefaultService(this.request);
        this.emailTask = new EmailTaskService(this.request);
        this.gc = new GcService(this.request);
        this.gen = new GenService(this.request);
        this.getSummaries = new GetSummariesService(this.request);
        this.habit = new HabitService(this.request);
        this.inboxTask = new InboxTaskService(this.request);
        this.init = new InitService(this.request);
        this.loadProgressReporterToken = new LoadProgressReporterTokenService(this.request);
        this.loadTopLevelInfo = new LoadTopLevelInfoService(this.request);
        this.login = new LoginService(this.request);
        this.metric = new MetricService(this.request);
        this.person = new PersonService(this.request);
        this.project = new ProjectService(this.request);
        this.report = new ReportService(this.request);
        this.search = new SearchService(this.request);
        this.slackTask = new SlackTaskService(this.request);
        this.smartList = new SmartListService(this.request);
        this.user = new UserService(this.request);
        this.vacation = new VacationService(this.request);
        this.workspace = new WorkspaceService(this.request);
    }
}

